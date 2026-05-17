import sqlite3
import pandas as pd
import geopandas as gpd
import os
from typing import Dict, List, Tuple, Optional
import yaml
import csv, json
import tempfile
import shutil
  
class database:
 
    # --------------------------------------------------
    # CONFIG
    # --------------------------------------------------
 
    TABLES_WITH_DESCRIPTIONS={"Indicators": {"configuration_table":"indicators",
                                             "description_column":"IndicatorDescription"},
                            "Seasons":{"configuration_table":"seasons",
                                             "description_column":"SeasonDescription"},
                            "Periods":{"configuration_table":"periods",
                                             "description_column":"PeriodDescription"}}

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
        config_file: str,
        tempDir: str
    ):
        #Load configuration file and populate self from there
        self.config_file=config_file
        with open(config_file, "r") as f:
            self.config = yaml.safe_load(f)

        #Setup paths
        self.db_path=tempfile.NamedTemporaryFile(dir=tempDir,
                                                delete=False,
                                                prefix="KAPy_database_",
                                                suffix=".sqlite").name
        print("TEMPORARY PATH: ",self.db_path)


        self.db_output_path = self.config['outputs']['database']

        #Populate rest of object
        self.stats_csv = self.config['outputs']['ensembleStatisticsCSV']
        self.members_csv = self.config['outputs']['ensembleMembersCSV']
        self.geometry = self.config['arealstats']['shapefile']
        self.include_geometry = (self.config['arealstats']['shapefile'] is not None)
 
        self.conn = None
        self._stats_df = None
        self._members_df = None
 
        os.makedirs(os.path.dirname(self.db_output_path) or ".", exist_ok=True)
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
 
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
            self._stats_df = pd.read_csv(self.stats_csv, encoding="windows-1252",keep_default_na=False,dtype="str")
        return self._stats_df
 
    def _load_members(self):
        if not self.members_csv:
            return None
        if self._members_df is None:
            print("Loading members CSV...")
            self._members_df = pd.read_csv(self.members_csv, encoding="windows-1252",keep_default_na=False,dtype="str")
        return self._members_df
 
    # --------------------------------------------------
    # SCHEMA
    # --------------------------------------------------
 
    def create_database_schema(self):
        #Create lookup tables. Data tables are created later in
        #create_data_tables(), once all referenced parent tables exist.
        conn = self.connect()
        cur = conn.cursor()
 
        for key,cfg in self.LOOKUP_TABLES.items():
            if key in self.TABLES_WITH_DESCRIPTIONS.keys():
                cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {cfg['table']}(
                    {cfg['id']} INTEGER PRIMARY KEY,
                    {cfg['code']} TEXT UNIQUE NOT NULL,
                    {self.TABLES_WITH_DESCRIPTIONS[key]['description_column']} TEXT
                );
                """)
            else:
                cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {cfg['table']}(
                    {cfg['id']} INTEGER PRIMARY KEY,
                    {cfg['code']} TEXT UNIQUE NOT NULL
                );
                """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS Configuration(
            id INTEGER PRIMARY KEY,
            ConfigurationType TEXT UNIQUE NOT NULL,
            FilePath TEXT UNIQUE NOT NULL,                    
            JSON TEXT UNIQUE NOT NULL
        );
        """)

        conn.commit()
 
    def create_data_tables(self):
        #Create Ensemble_stats and Ensemble_members with FK references.
        #Must be called after all referenced parent tables have been created
        #(Indicators, Time_Periods, Seasons via import_metadata; lookup tables
        #via build_lookup_tables; Areas via import_geometries).
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
 
    def import_descriptions(self):
        conn = self.connect()
        cur = conn.cursor()

        for key in self.TABLES_WITH_DESCRIPTIONS.keys():
            #Import configuration table, drop disabled
            tbl= self.LOOKUP_TABLES[key]
            desc_tbl=self.TABLES_WITH_DESCRIPTIONS[key]
            cfg = pd.read_csv(self.config['configurationTables'][desc_tbl['configuration_table']],
                               sep="\t",
                                encoding="windows-1252",
                                dtype=str)
            cfg=cfg[cfg['enabled'] !=""]

            #Handle Indicator codes, which are specified as a comma-separated list, separately.
            if key =="Indicators":
                cfg['id'] = cfg["indicator_codes"].apply(lambda x: [item.strip() for item in x.split(",")] if pd.notnull(x) else [])
                cfg=cfg.explode("id")
            cfg=cfg[["id","description"]]
            cfg=cfg.rename(columns={"id": tbl['code'],
                                    "description":desc_tbl['description_column']})

            #Import from database
            df = pd.read_sql(f"SELECT * FROM {tbl["table"]}", conn)
            df=df.drop(columns=desc_tbl['description_column'])

            #Left join
            df_joined = df.merge(cfg, on=tbl["code"], how="left")

            #Write back to database
            df_joined.to_sql(f"{tbl["table"]}", conn, index=False, if_exists="replace")
 
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
        if self.conn:
            self.conn.close()
            self.conn = None
 
        gdf = gpd.read_file(self.geometry)
        gdf["AreaKey"] = gdf.index
 
        gdf.to_file(self.db_path, layer="Areas", driver="GPKG", engine="pyogrio", fid="AreaKey")
 
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys=ON;")
 
    # --------------------------------------------------
    # MAPPINGS
    # --------------------------------------------------
 
    def build_mappings(self):
        conn = self.connect()
        maps = {}
 
        for name,cfg in self.LOOKUP_TABLES.items():
            df = pd.read_sql_query(f"SELECT {cfg['id']},{cfg['code']} FROM {cfg['table']}", conn)
            maps[name] = {r[cfg["code"]]: r[cfg["id"]] for _,r in df.iterrows()}

        return maps
 
    # --------------------------------------------------
    # PROCESSING
    # --------------------------------------------------
 
    def process_stats(self, maps):
        df=self._load_stats().copy()
 
        #Apply mappings
        df["AreaKey"]=df.areaID.replace("NA", -999).astype(int).replace(-999,None)
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
        df["AreaKey"]=df.areaID.replace("NA", -999).astype(int).replace(-999,None)
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
 
    def import_configuration(self):
        conn = self.connect()
        cur = conn.cursor()

        #Import configuration yaml
        cur.execute("""
        INSERT INTO Configuration 
        VALUES (NULL, 'config', ?,?)
        """, (self.config_file, json.dumps(self.config)))

        #Loop over configuration tables
        for key,path in self.config['configurationTables'].items():
            if (path is None) or (path==''):
                continue
            #Load configuration table
            tbl=pd.read_csv(path, 
                            sep="\t",
                            encoding="windows-1252",
                            keep_default_na=False,
                            dtype="str")
            tbl=tbl[tbl['enabled'] !=""]
            cur.execute("""
            INSERT INTO Configuration 
            VALUES (NULL, ?, ?,?)
            """, (key, self.config["configurationTables"][key], tbl.to_json()))
            

        conn.commit()

    
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
            i.IndicatorDescription  AS IndicatorDescription,
            es.AreaKey              AS AreaKey,
            p.PeriodCode            AS PeriodCode,
            p.PeriodDescription     AS PeriodDescription,
            se.SeasonCode           AS SeasonCode,
            se.SeasonDescription    AS SeasonDescription,
            ar.ArealStatisticCode   AS ArealStatisticCode,
            es.Delta                AS Delta,
            es.Percentile           AS Percentile,
            es.Value                AS Value
        FROM Ensemble_statistics AS es
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
            i.IndicatorDescription  AS IndicatorDescription,
            em.AreaKey              AS AreaKey,
            p.PeriodCode            AS PeriodCode,
            p.PeriodDescription     AS PeriodDescription,
            se.SeasonCode           AS SeasonCode,
            se.SeasonDescription    AS SeasonDescription,
            ar.ArealStatisticCode   AS ArealStatisticCode,
            em.Delta                AS Delta,
            em.Value                AS Value
        FROM Indicator_data AS em
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
        # But only if we have geometry in the first place.
        if self.include_geometry:
            for view_name in ("view_Ensemble_statistics", "view_Indicator_data"):
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
            if self.include_geometry:
                self.import_geometries()
 
            self.create_database_schema()
            self.build_lookup_tables()
            self.create_data_tables()
            self.import_descriptions()
            self.import_stats()
            self.import_members()
            self.import_configuration()
            self.create_indexes_and_views()
            print("\nSUCCESS")
        finally:
            self.close()
        
        #Move the result into place
        #Delete DB if it already exists
        if os.path.exists(self.db_output_path):  
            os.remove(self.db_output_path)
        shutil.move(self.db_path, self.db_output_path)
 

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

    configfile="./config/config.yaml"
    #configfile="./workflow/testing/config.yaml"

    db = database(config_file=configfile)
    
    try:
        db.create_full_database()
    except ValueError as e:
        print(f"Validation Error: {e}")
    except FileNotFoundError as e:
        print(f"File Error: {e}")
    finally:
        db.close()
        



        
        
        
