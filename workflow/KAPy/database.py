import sqlite3
import pandas as pd
import geopandas as gpd
import os
from typing import Dict, List, Tuple, Optional
 
 
class database:
 
    # --------------------------------------------------
    # CONFIG
    # --------------------------------------------------
 
    METADATA_TABLE_MAP = {
        'indicators_tsv': 'Indicators2',
        'time_periods_tsv': 'Time_Periods2',
        'seasons_tsv': 'Seasons2',
    }
 
    LOOKUP_TABLES = {
        "Seasons": dict(table="Seasons", id="SeasonKey", code="SeasonCode", src="seasonID"),
        "Periods": dict(table="Periods", id="PeriodKey", code="PeriodCode", src="periodID"),
        "Indicators": dict(table="Indicators", id="IndicatorKey", code="IndicatorCode", src="indID"),
        "Scenarios": dict(table="Scenarios", id="ScenarioKey", code="ScenarioCode", src="expt"),
        "Grids": dict(table="Grids", id="GridKey", code="GridCode", src="gridID"),
        "Members": dict(table="Members", id="MemberKey", code="MemberCode", src="memberID"),
        "Datasets": dict(table="Datasets", id="DatasetKey", code="DatasetCode", src="datasetID"),
        "ArealStatistics": dict(table="ArealStatistics", id="ArealStatisticKey", code="ArealStatisticCode", src="arealStatistic"),
    }
 
    # --------------------------------------------------
    # INIT
    # --------------------------------------------------
 
    def __init__(
        self,
        output_gpkg_path: str,
        indicators_tsv: str,
        time_periods_tsv: str,
        seasons_tsv: str,
        ensemble_stats_csv: str,
        ensemble_members_csv: Optional[str] = None,
        geometry: Optional[str] = None,
        include_geometry: bool = False,
    ):
        self.db_path = output_gpkg_path
        self.stats_csv = ensemble_stats_csv[0]
        self.members_csv = ensemble_members_csv[0]
        self.geometry = geometry
        self.include_geometry = include_geometry
 
        self.metadata_tsv_files = {
            'indicators_tsv': indicators_tsv,
            'time_periods_tsv': time_periods_tsv,
            'seasons_tsv': seasons_tsv,
        }
 
        self.conn = None
        self._stats_df = None
        self._members_df = None
 
        self._validate_paths()
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
 
    # --------------------------------------------------
    # FILE VALIDATION
    # --------------------------------------------------
 
    def _validate_paths(self):
        missing = []
 
        for p in self.metadata_tsv_files.values():
            if not os.path.exists(p):
                missing.append(p)
 
        if not os.path.exists(self.stats_csv):
            missing.append(self.stats_csv)
 
        if self.members_csv and not os.path.exists(self.members_csv):
            missing.append(self.members_csv)
 
        if self.include_geometry:
            if not self.geometry:
                missing.append("<geometry> path not provided")
            elif not os.path.exists(self.geometry):
                missing.append(self.geometry)
 
        if missing:
            raise FileNotFoundError("\n".join(missing))
 
    # --------------------------------------------------
    # CONNECTION
    # --------------------------------------------------
 
    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.execute("PRAGMA foreign_keys=ON;")
        return self.conn
 
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
 
    # --------------------------------------------------
    # CSV LOADERS
    # --------------------------------------------------
 
    def _load_stats(self):
        if self._stats_df is None:
            print("Loading stats CSV...")
            self._stats_df = pd.read_csv(self.stats_csv, encoding="windows-1252")
        return self._stats_df
 
    def _load_members(self):
        if not self.members_csv:
            return None
        if self._members_df is None:
            print("Loading members CSV...")
            self._members_df = pd.read_csv(self.members_csv, encoding="windows-1252")
        return self._members_df
 
    # --------------------------------------------------
    # SCHEMA
    # --------------------------------------------------
 
    def create_database_schema(self):
        """Create lookup tables and Version. Data tables are created later in
        create_data_tables(), once all referenced parent tables exist."""
        conn = self.connect()
        cur = conn.cursor()
 
        for cfg in self.LOOKUP_TABLES.values():
            cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {cfg['table']}(
                {cfg['id']} INTEGER PRIMARY KEY,
                {cfg['code']} TEXT UNIQUE NOT NULL
            );
            """)
 
        cur.execute("CREATE TABLE IF NOT EXISTS Version(version TEXT);")
        conn.commit()
 
    def create_data_tables(self):
        """Create Ensemble_stats and Ensemble_members with FK references.
        Must be called after all referenced parent tables have been created
        (Indicators, Time_Periods, Seasons via import_metadata; lookup tables
        via build_lookup_tables; Areas via import_geometries)."""
        conn = self.connect()
        cur = conn.cursor()
 
        cur.execute("""
        CREATE TABLE IF NOT EXISTS Ensemble_statistics (
            id               INTEGER PRIMARY KEY,
            DatasetKey        INTEGER  REFERENCES Datasets(DatasetKey),
            ScenarioKey       INTEGER  REFERENCES Scenarios(ScenarioKey),
            GridKey           INTEGER  REFERENCES Grids(GridKey),
            IndicatorKey      INTEGER  REFERENCES Indicators(IndicatorKey),
            AreaKey           INTEGER  REFERENCES Areas(AreaKey),
            PeriodKey         INTEGER  REFERENCES Time_Periods(PeriodKey),
            SeasonKey         INTEGER  REFERENCES Seasons(SeasonKey),
            Delta            BOOLEAN,
            ArealStatisticKey INTEGER  REFERENCES ArealStatistics(ArealStatisticKey),
            Percentile       REAL,
            Value            REAL
        );
        """)
 
        cur.execute("""
        CREATE TABLE IF NOT EXISTS Indicator_data(
            id               INTEGER PRIMARY KEY,
            DatasetKey        INTEGER  REFERENCES Datasets(DatasetKey),
            MemberKey         INTEGER  REFERENCES Members(MemberKey),
            ScenarioKey       INTEGER  REFERENCES Scenarios(ScenarioKey),
            GridKey           INTEGER  REFERENCES Grids(GridKey),
            IndicatorKey      INTEGER  REFERENCES Indicators(IndicatorKey),
            AreaKey           INTEGER  REFERENCES Areas(AreaKey),
            PeriodKey         INTEGER  REFERENCES Time_Periods(PeriodKey),
            SeasonKey         INTEGER  REFERENCES Seasons(SeasonKey),
            Delta            BOOLEAN,
            ArealStatisticKey INTEGER  REFERENCES ArealStatistics(ArealStatisticKey),
            Value            REAL
        );
        """)
 
        conn.commit()
 
    # --------------------------------------------------
    # METADATA IMPORT
    # --------------------------------------------------
 
    def _infer_type(self, s):
        if pd.api.types.is_integer_dtype(s): return "INTEGER"
        if pd.api.types.is_float_dtype(s): return "REAL"
        return "TEXT"
 
    def import_metadata(self):
        conn = self.connect()
        cur = conn.cursor()
 
        for key, table in self.METADATA_TABLE_MAP.items():
            df = pd.read_csv(self.metadata_tsv_files[key], sep="\t", encoding="windows-1252")
 
            if table == "Indicators":
                df = df.rename(columns={"id": "IndicatorKey"})
 
            if table == "Seasons":
                df = df.rename(columns={"id": "SeasonCode"})
                df.insert(0, "SeasonKey", range(1, len(df) + 1))
 
            if table == "Time_Periods":
                df = df.rename(columns={"id": "PeriodKey", "name": "PeriodCode"})
 
            cols = []
            for c in df.columns:
                t = self._infer_type(df[c])
                if c.lower().endswith("key"):
                    cols.append(f"{c} {t} PRIMARY KEY")
                else:
                    cols.append(f"{c} {t}")
 
            cur.execute(f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(cols)})")
 
            cur.executemany(
                f"INSERT INTO {table} VALUES ({','.join(['?']*len(df.columns))})",
                df.itertuples(index=False, name=None),
            )
 
        conn.commit()
 
    # --------------------------------------------------
    # LOOKUP TABLES (UNION OF BOTH CSVs)
    # --------------------------------------------------
 
    def build_lookup_tables(self):
        dfs = [self._load_stats()]
        mem = self._load_members()
        if mem is not None:
            dfs.append(mem)
 
        conn = self.connect()
        cur = conn.cursor()
 
        for cfg in self.LOOKUP_TABLES.values():
            codes = pd.concat([d[cfg["src"]].astype(str) for d in dfs if cfg["src"] in d.columns])
            codes = sorted(codes.unique())
            rows = [(i+1,c) for i,c in enumerate(codes)]
 
            cur.executemany(
                f"INSERT INTO {cfg['table']} ({cfg['id']},{cfg['code']}) VALUES (?,?)",
                rows,
            )
            print(cfg["table"], len(rows))
 
        conn.commit()
 
    # --------------------------------------------------
    # AREAS
    # --------------------------------------------------
 
    def import_geometries(self):
        if not self.include_geometry:
            return self._create_areas_table()
 
        if self.conn:
            self.conn.close()
            self.conn = None
 
        gdf = gpd.read_file(self.geometry)
        gdf["AreaKey"] = gdf.index
 
        gdf.to_file(self.db_path, layer="Areas", driver="GPKG", engine="pyogrio", fid="AreaKey")
 
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys=ON;")
 
    def _create_areas_table(self):
        dfs = [self._load_stats()]
        mem = self._load_members()
        if mem is not None:
            dfs.append(mem)
 
        codes = pd.concat([d["areaID"].astype(str) for d in dfs]).unique()
        codes = sorted(codes)
 
        conn = self.connect()
        cur = conn.cursor()
 
        cur.execute("""
        CREATE TABLE IF NOT EXISTS Areas(
            AreaKey INTEGER PRIMARY KEY,
            AreaCode TEXT UNIQUE
        );
        """)
 
        cur.executemany("INSERT INTO Areas VALUES (?,?)",
            [(i+1,c) for i,c in enumerate(codes)]
        )
 
        conn.commit()
 
    # --------------------------------------------------
    # MAPPINGS
    # --------------------------------------------------
 
    def build_mappings(self):
        conn = self.connect()
        maps = {}
 
        for name,cfg in self.LOOKUP_TABLES.items():
            df = pd.read_sql_query(f"SELECT {cfg['id']},{cfg['code']} FROM {cfg['table']}", conn)
            maps[name] = {r[cfg["code"]]: r[cfg["id"]] for _,r in df.iterrows()}

        if not self.include_geometry:
            df = pd.read_sql_query("SELECT AreaKey,AreaCode FROM Areas", conn)
            maps["Areas"] = dict(zip(df.AreaCode.astype(str), df.AreaKey))
 
        return maps
 
    # --------------------------------------------------
    # PROCESSING
    # --------------------------------------------------
 
    def process_stats(self, maps):
        df=self._load_stats().copy()
 
        #Apply mappings
        df["AreaKey"]=df.areaID.astype(int)
        df["Percentile"]=df["percentiles"].astype(float)
        for lookup_dict in self.LOOKUP_TABLES.values():
            df[lookup_dict["id"]]= df[lookup_dict["src"]].astype(str).map(maps[lookup_dict["table"]])

        #Pivot delta columns longer
        base=df[df.indicator_mean.notna()].copy()
        base["Value"]=base.indicator_mean
        base["Delta"]=False
 
        delta=df[df.delta_mean.notna()].copy()
        delta["Value"]=delta.delta_mean
        delta["Delta"]=True
 
        df=pd.concat([base,delta])
 
        # Output
        # Get list of column names and order from the existing table - use this to filter df
        cursor = self.conn.execute("PRAGMA table_info(Ensemble_statistics);")
        columns = cursor.fetchall()
        output_columns = [col[1] for col in columns if col[1] != "id"]
        df=df[output_columns]

        return list(df.itertuples(index=False,name=None))
 
    def process_members(self, maps):
        df=self._load_members().copy()
 
        #Apply mappings
        df["AreaKey"]=df.areaID.astype(int)
        for lookup_dict in self.LOOKUP_TABLES.values():
            df[lookup_dict["id"]]= df[lookup_dict["src"]].astype(str).map(maps[lookup_dict["table"]])
 
        base=df[df.indicator.notna()].copy()
        base["Value"]=base.indicator
        base["Delta"]=False
 
        delta=df[df.delta.notna()].copy()
        delta["Value"]=delta.delta
        delta["Delta"]=True
 
        df=pd.concat([base,delta])
 
        # Output
        # Get list of column names and order from the existing table - use this to filter df
        cursor = self.conn.execute("PRAGMA table_info(Indicator_data);")
        columns = cursor.fetchall()
        output_columns = [col[1] for col in columns if col[1] != "id"]
        df=df[output_columns]

        df=df[output_columns]
 
        return list(df.itertuples(index=False,name=None))
 
    # --------------------------------------------------
    # INSERTS
    # --------------------------------------------------
 
    def import_stats(self):
        rows=self.process_stats(self.build_mappings())
        conn=self.connect()
        conn.execute("PRAGMA foreign_keys=OFF;")
        cur=conn.cursor()
 
        #Data order is taken from the table, so no need to worry about specify the column names here
        cur.executemany("""
        INSERT INTO Ensemble_statistics
        VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?)
        """,rows)
 
        conn.commit()
        conn.execute("PRAGMA foreign_keys=ON;")
        print("Inserted stats:",len(rows))
 
    def import_members(self):
        if not self.members_csv:
            return
 
        rows=self.process_members(self.build_mappings())
        conn=self.connect()
        conn.execute("PRAGMA foreign_keys=OFF;")
        cur=conn.cursor()
 
        #Data order is taken from the database table, so no need to worry about specify the column names here
        cur.executemany("""
        INSERT INTO Indicator_data
        VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?)
        """,rows)
 
        conn.commit()
        conn.execute("PRAGMA foreign_keys=ON;")
        print("Inserted members:",len(rows))
 
    # --------------------------------------------------
    # INDEXES AND VIEWS
    # --------------------------------------------------
 
    def create_indexes_and_views(self):
        conn = self.connect()
        cur = conn.cursor()
 
        # -- Indexes on Ensemble_stats --
        cur.execute("CREATE INDEX IF NOT EXISTS idx_stats_area        ON Ensemble_statistics(AreaKey);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_stats_indicator   ON Ensemble_statistics(IndicatorKey);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_stats_scenario    ON Ensemble_statistics(ScenarioKey);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_stats_period      ON Ensemble_statistics(PeriodKey);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_stats_season      ON Ensemble_statistics(SeasonKey);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_stats_grid        ON Ensemble_statistics(GridKey);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_stats_dataset      ON Ensemble_statistics(DatasetKey);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_stats_arealstat   ON Ensemble_statistics(ArealStatisticKey);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_stats_delta       ON Ensemble_statistics(Delta);")
        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_stats_composite
            ON Ensemble_statistics(IndicatorKey, ScenarioKey, PeriodKey, SeasonKey, Delta);
        """)
 
        # -- Indexes on Ensemble_members --
        cur.execute("CREATE INDEX IF NOT EXISTS idx_mem_area          ON Indicator_data(AreaKey);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_mem_indicator     ON Indicator_data(IndicatorKey);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_mem_scenario      ON Indicator_data(ScenarioKey);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_mem_period        ON Indicator_data(PeriodKey);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_mem_season        ON Indicator_data(SeasonKey);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_mem_dataset       ON Indicator_data(DatasetKey);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_mem_grid          ON Indicator_data(GridKey);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_mem_member        ON Indicator_data(MemberKey);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_mem_arealstat     ON Indicator_data(ArealStatisticKey);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_mem_delta         ON Indicator_data(Delta);")
        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_mem_composite
            ON Indicator_data(IndicatorKey, ScenarioKey, PeriodKey, SeasonKey, Delta);
        """)
 
        # -- View: Ensemble_stats with all metadata decoded --
        cur.execute("""
        CREATE VIEW IF NOT EXISTS view_Ensemble_statistics AS
        SELECT
            es.id                   AS id,
            ds.DatasetCode          AS DatasetCode,
            sc.ScenarioCode         AS ScenarioCode,
            gr.GridCode             AS GridCode,
            i.IndicatorCode         AS IndicatorCode,
            es.AreaKey              AS AreaKey,
            p.PeriodCode            AS PeriodCode,
            se.SeasonCode           AS SeasonCode,
            ar.ArealStatisticCode   AS ArealStatisticCode,
            es.Delta                AS Delta,
            es.Percentile           AS Percentile,
            es.Value                AS Value
        FROM Ensemble_statistics AS es
        JOIN Areas           AS a  ON es.AreaKey           = a.AreaKey
        JOIN Indicators      AS i  ON es.IndicatorKey      = i.IndicatorKey
        JOIN Scenarios       AS sc ON es.ScenarioKey       = sc.ScenarioKey
        JOIN Periods         AS p  ON es.PeriodKey         = p.PeriodKey
        JOIN Seasons         AS se ON es.SeasonKey         = se.SeasonKey
        JOIN Grids           AS gr ON es.GridKey           = gr.GridKey
        JOIN Datasets        AS ds ON es.DatasetKey        = ds.DatasetKey
        JOIN ArealStatistics AS ar ON es.ArealStatisticKey = ar.ArealStatisticKey;
        """)
 
        # -- View: Ensemble_members with all metadata decoded --
        cur.execute("""
        CREATE VIEW IF NOT EXISTS view_Indicator_data AS
        SELECT
            em.id                   AS id,
            ds.DatasetCode          AS DatasetCode,
            me.MemberCode           AS MemberCode,
            sc.ScenarioCode         AS ScenarioCode,
            gr.GridCode             AS GridCode,
            i.IndicatorCode         AS IndicatorCode,
            em.AreaKey              AS AreaKey,
            p.PeriodCode            AS PeriodCode,
            se.SeasonCode           AS SeasonCode,
            ar.ArealStatisticCode   AS ArealStatisticCode,
            em.Delta                AS Delta,
            em.Value                AS Value
        FROM Indicator_data AS em
        JOIN Areas           AS a  ON em.AreaKey           = a.AreaKey
        JOIN Indicators      AS i  ON em.IndicatorKey      = i.IndicatorKey
        JOIN Scenarios       AS sc ON em.ScenarioKey       = sc.ScenarioKey
        JOIN Periods         AS p  ON em.PeriodKey         = p.PeriodKey
        JOIN Seasons         AS se ON em.SeasonKey         = se.SeasonKey
        JOIN Datasets        AS ds ON em.DatasetKey        = ds.DatasetKey
        JOIN Grids           AS gr ON em.GridKey           = gr.GridKey
        JOIN Members         AS me ON em.MemberKey         = me.MemberKey
        JOIN ArealStatistics AS ar ON em.ArealStatisticKey = ar.ArealStatisticKey;
        """)
 
        conn.commit()
 
        # Register views in gpkg_contents so GeoPackage-aware clients
        # (QGIS, ArcGIS, etc.) can discover and display them.
        for view_name in ("view_Ensemble_stats", "view_Ensemble_members"):
            cur.execute("""
            INSERT OR REPLACE INTO gpkg_contents
                (table_name, data_type, identifier, description, srs_id)
            VALUES (?, 'attributes', ?, '', NULL)
            """, (view_name, view_name))
 
        conn.commit()
        print("Indexes and views created.")
 
    # --------------------------------------------------
    # PIPELINE
    # --------------------------------------------------
 
    def create_full_database(self):
        try:
            #Delete DB if it already exists
            if os.path.exists(self.db_path):  
                os.remove(self.db_path)

            self.import_geometries()
            self.create_database_schema()
            self.import_metadata()
            self.build_lookup_tables()
            self.create_data_tables()
            self.import_stats()
            self.import_members()
            self.create_indexes_and_views()
            print("\nSUCCESS")
        finally:
            self.close()
 

#--------------------------------------------
# Example usage
# -------------------------------------------

if __name__ == "__main__":
    #Setup for debugging with VS code 
    #Assumes a working directory
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    import KAPy

    #config=KAPy.getConfig("./config/config.yaml")  
    config=KAPy.getConfig("./workflow/testing/config.yaml")  

    db = database(
        output_gpkg_path=config['outputs']['database'],
        indicators_tsv=config['configurationTables']['indicators'],
        time_periods_tsv=config['configurationTables']['periods'],
        seasons_tsv=config['configurationTables']['seasons'],
        ensemble_stats_csv=config['outputs']['ensembleStatisticsCSV'],
        ensemble_members_csv=config['outputs']['ensembleMembersCSV'],
        geometry=config['arealstats']['shapefile'],
        include_geometry=True,
    )
    
    try:
        db.create_full_database()
    except ValueError as e:
        print(f"Validation Error: {e}")
    except FileNotFoundError as e:
        print(f"File Error: {e}")
    finally:
        db.close()
        



        
        
        
