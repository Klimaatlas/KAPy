import sqlite3
import pandas as pd
import geopandas as gpd
import os
import json
import tempfile
import shutil
from pathlib import Path
from KAPy import helpers
from KAPy import config
from KAPy import workflow


class database:

    # --------------------------------------------------
    # CONFIG
    # --------------------------------------------------

    TABLES_WITH_DESCRIPTIONS = {
        "Indicators": {
            "configuration_table": "indicators",
            "description_column": "IndicatorDescription",
        },
        "Seasons": {
            "configuration_table": "seasons",
            "description_column": "SeasonDescription",
        },
        "TimeBins": {
            "configuration_table": "periods",
            "description_column": "TimeBinDescription",
        },
    }

    LOOKUP_TABLES = {
        "Seasons": dict(
            table="Seasons", id="SeasonKey", code="SeasonCode", src="seasonID"
        ),
        "TimeBins": dict(
            table="TimeBins", id="TimeBinKey", code="TimeBinCode", src="timeBinID"
        ),
        "Indicators": dict(
            table="Indicators", id="IndicatorKey", code="IndicatorCode", src="indID"
        ),
        "Scenarios": dict(
            table="Scenarios", id="ScenarioKey", code="ScenarioCode", src="expt"
        ),
        "Grids": dict(table="Grids", id="GridKey", code="GridCode", src="gridID"),
        "Members": dict(
            table="Members", id="MemberKey", code="MemberCode", src="memberID"
        ),
        "Datasets": dict(
            table="Datasets", id="DatasetKey", code="DatasetCode", src="datasetID"
        ),
        "StatisticTypes": dict(
            table="StatisticTypes",
            id="StatisticTypeKey",
            code="StatisticTypeCode",
            src="statisticType",
        ),
    }

    PIPELINE_STEPS = {"indicators": 5, "regrid": 6, "ensstats": 7}

    # --------------------------------------------------
    # INIT
    # --------------------------------------------------

    def __init__(self, config_file: str, tempDir: str):
        # Load configuration file and populate self from there
        self.config_file = config_file
        self.config = config.get_config(self.config_file)

        # Then add the workflow configuration
        self.workflow = workflow.get_workflow(self.config)

        # Setup paths
        self.db_path = tempfile.NamedTemporaryFile(
            dir=tempDir, delete=False, prefix="KAPy_database_", suffix=".sqlite"
        ).name
        print("TEMPORARY PATH: ", self.db_path)

        OUTPUT_PATHS = helpers.get_OUTPUT_PATHS(self.config["output_directory"])

        self.db_output_path = OUTPUT_PATHS["database"]

        # Handle situations where the areal statistics are not requested
        if self.config["areal_statistics"]["ensemble_areal_statistics"]:
            self.ensemble_stats_csv = OUTPUT_PATHS["ensemble_areal_statistics_csv"]
        else:
            self.ensemble_stats_csv = None
        if self.config["areal_statistics"]["member_areal_statistics"]:
            self.member_stats_csv = OUTPUT_PATHS["member_areal_statistics_csv"]
        else:
            self.member_stats_csv = None

        # Populate rest of object
        self.geometry = self.config["areal_statistics"]["shapefile"]
        self.include_geometry = self.config["areal_statistics"]["shapefile"] is not None

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
    # SCHEMA
    # --------------------------------------------------

    def create_database_schema(self):
        # Create lookup tables. Data tables are created later in
        # create_data_tables(), once all referenced parent tables exist.
        conn = self.connect()
        cur = conn.cursor()

        for key, cfg in self.LOOKUP_TABLES.items():
            if key in self.TABLES_WITH_DESCRIPTIONS.keys():
                cur.execute(
                    f"""
                CREATE TABLE IF NOT EXISTS {cfg['table']}(
                    {cfg['id']} INTEGER PRIMARY KEY,
                    {cfg['code']} TEXT UNIQUE NOT NULL,
                    {self.TABLES_WITH_DESCRIPTIONS[key]['description_column']} TEXT
                );
                """
                )
            else:
                cur.execute(
                    f"""
                CREATE TABLE IF NOT EXISTS {cfg['table']}(
                    {cfg['id']} INTEGER PRIMARY KEY,
                    {cfg['code']} TEXT UNIQUE NOT NULL
                );
                """
                )

        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS Configuration(
            id INTEGER PRIMARY KEY,
            ConfigurationType TEXT UNIQUE NOT NULL,
            FilePath TEXT UNIQUE NOT NULL,                    
            JSON TEXT UNIQUE NOT NULL
        );
        """
        )

        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS PipelineSteps(
            PipelineStepKey INTEGER PRIMARY KEY,
            PipelineStepCode TEXT UNIQUE NOT NULL
        );
        """
        )

        conn.commit()

    def create_data_tables(self):
        # Create Ensemble_stats and Ensemble_members with FK references.
        # Must be called after all referenced parent tables have been created
        # (Indicators, TimeBins, Seasons via import_metadata; lookup tables
        # via build_lookup_tables; Areas via import_geometries).
        conn = self.connect()
        cur = conn.cursor()

        if self.ensemble_stats_csv is not None:
            cur.execute(
                """
            CREATE TABLE IF NOT EXISTS EnsembleArealStatistics (
                id               INTEGER PRIMARY KEY,
                DatasetKey        INTEGER  REFERENCES Datasets(DatasetKey),
                ScenarioKey       INTEGER  REFERENCES Scenarios(ScenarioKey),
                GridKey           INTEGER  REFERENCES Grids(GridKey),
                IndicatorKey      INTEGER  REFERENCES Indicators(IndicatorKey),
                AreaKey           INTEGER  REFERENCES Areas(AreaKey),
                TimeBinKey         INTEGER  REFERENCES TimeBins(TimeBinKey),
                SeasonKey         INTEGER  REFERENCES Seasons(SeasonKey),
                Delta            BOOLEAN,
                StatisticTypeKey INTEGER  REFERENCES StatisticTypes(StatisticTypeKey),
                Percentile       REAL,
                Value            REAL
            );
            """
            )

        if self.member_stats_csv is not None:
            cur.execute(
                """
            CREATE TABLE IF NOT EXISTS MemberArealStatistics(
                id               INTEGER PRIMARY KEY,
                DatasetKey        INTEGER  REFERENCES Datasets(DatasetKey),
                MemberKey         INTEGER  REFERENCES Members(MemberKey),
                ScenarioKey       INTEGER  REFERENCES Scenarios(ScenarioKey),
                GridKey           INTEGER  REFERENCES Grids(GridKey),
                IndicatorKey      INTEGER  REFERENCES Indicators(IndicatorKey),
                AreaKey           INTEGER  REFERENCES Areas(AreaKey),
                TimeBinKey         INTEGER  REFERENCES TimeBins(TimeBinKey),
                SeasonKey         INTEGER  REFERENCES Seasons(SeasonKey),
                Delta            BOOLEAN,
                StatisticTypeKey INTEGER  REFERENCES StatisticTypes(StatisticTypeKey),
                Value            REAL
            );
            """
            )

        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS GriddedFiles (
            id            INTEGER PRIMARY KEY,
            IndicatorKey  INTEGER REFERENCES Indicators(IndicatorKey),
            DatasetKey    INTEGER REFERENCES Datasets(DatasetKey),
            GridKey       INTEGER REFERENCES Grids(GridKey),
            ScenarioKey   INTEGER REFERENCES Scenarios(ScenarioKey),
            MemberKey     INTEGER REFERENCES Members(MemberKey),
            PipelineStep  INTEGER REFERENCES PipelineSteps(PipelineStepKey),
            Path      TEXT UNIQUE NOT NULL
        );
        """
        )
        conn.commit()

    # --------------------------------------------------
    # METADATA IMPORT
    # --------------------------------------------------

    def _infer_type(self, s):
        if pd.api.types.is_integer_dtype(s):
            return "INTEGER"
        if pd.api.types.is_float_dtype(s):
            return "REAL"
        return "TEXT"

    def import_descriptions(self):
        conn = self.connect()

        for key in self.TABLES_WITH_DESCRIPTIONS.keys():
            # Import configuration table, drop disabled
            tbl = self.LOOKUP_TABLES[key]
            desc_tbl = self.TABLES_WITH_DESCRIPTIONS[key]
            cfg = pd.read_csv(
                self.config["configuration_tables"][desc_tbl["configuration_table"]],
                sep="\t",
                encoding="windows-1252",
                dtype=str,
            )
            cfg = cfg[cfg["enabled"] != ""]

            # Handle Indicator codes, which are specified as a comma-separated list, separately.
            if key == "Indicators":
                # Use id if indicator codes is empty or NaN
                cfg["indicator_codes"] = [
                    (
                        rw["id"]
                        if pd.isna(rw["indicator_codes"]) or rw["indicator_codes"] == ""
                        else rw["indicator_codes"]
                    )
                    for _, rw in cfg.iterrows()
                ]
                # Split indicator codes into lists
                cfg["id"] = cfg["indicator_codes"].apply(
                    lambda x: (
                        [item.strip() for item in x.split(",")] if pd.notna(x) else [x]
                    )
                )
                cfg = cfg.explode("id")
            cfg = cfg[["id", "description"]]
            cfg = cfg.rename(
                columns={
                    "id": tbl["code"],
                    "description": desc_tbl["description_column"],
                }
            )

            # Import from database
            df = pd.read_sql(f'SELECT * FROM {tbl["table"]}', conn)
            df = df.drop(columns=desc_tbl["description_column"])

            # Left join
            df_joined = df.merge(cfg, on=tbl["code"], how="left")

            # Write back to database
            df_joined.to_sql(f"{tbl['table']}", conn, index=False, if_exists="replace")

        conn.commit()

    # --------------------------------------------------
    # AREAS
    # --------------------------------------------------

    def import_geometries(self):
        # Close any existing connection so we can safely overwrite the DB
        if self.conn:
            self.conn.close()
            self.conn = None

        gdf = gpd.read_file(self.geometry)
        gdf = gdf.reset_index(drop=True)
        gdf.index.name = "AreaKey"

        # Convert geometry to WKT strings
        gdf["geom_wkt"] = gdf.geometry.apply(
            lambda geom: geom.wkt if geom is not None else None
        )

        # Store the CRS as a column; same value for all rows
        gdf["geom_crs"] = gdf.crs.to_wkt() if gdf.crs is not None else None

        # Create / connect DB
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys=ON;")

        # Write the entire GeoDataFrame (minus geometry) to a normal table
        # This creates (or replaces) the Areas table with all columns from df.
        df = gdf.drop(columns="geometry")
        df.to_sql("Areas", self.conn, if_exists="replace", index=True)

        self.conn.commit()

    # --------------------------------------------------
    # CSV LOADERS
    # --------------------------------------------------

    def _load_stats(self):
        if self.ensemble_stats_csv is None:
            return None
        if self._stats_df is None:
            print("Loading stats CSV...")
            self._stats_df = pd.read_csv(
                self.ensemble_stats_csv,
                encoding="windows-1252",
                keep_default_na=False,
                dtype="str",
            )
        return self._stats_df

    def _load_members(self):
        if self.member_stats_csv is None:
            return None
        if self._members_df is None:
            print("Loading members CSV...")
            self._members_df = pd.read_csv(
                self.member_stats_csv,
                encoding="windows-1252",
                keep_default_na=False,
                dtype="str",
            )
        return self._members_df

    # --------------------------------------------------
    # LOOKUP TABLES (UNION OF BOTH CSVs)
    # --------------------------------------------------

    def build_lookup_tables(self):
        if self.ensemble_stats_csv is None:
            return
        dfs = [self._load_stats()]
        mem = self._load_members()
        if mem is not None:
            dfs.append(mem)

        conn = self.connect()
        cur = conn.cursor()

        for cfg in self.LOOKUP_TABLES.values():
            codes = pd.concat(
                [d[cfg["src"]].astype(str) for d in dfs if cfg["src"] in d.columns]
            )
            codes = sorted(codes.unique())
            rows = [(i + 1, c) for i, c in enumerate(codes)]

            cur.executemany(
                f"INSERT INTO {cfg['table']} ({cfg['id']},{cfg['code']}) VALUES (?,?)",
                rows,
            )
            print(cfg["table"], len(rows))

        conn.commit()

    def build_pipelineSteps_lookup(self):
        conn = self.connect()
        cur = conn.cursor()

        for code, key in self.PIPELINE_STEPS.items():
            cur.execute(
                "INSERT OR IGNORE INTO PipelineSteps (PipelineStepKey, PipelineStepCode) VALUES (?, ?)",
                (key, code),
            )

        conn.commit()

    # --------------------------------------------------
    # MAPPINGS
    # --------------------------------------------------

    def build_mappings(self):
        conn = self.connect()
        maps = {}

        for name, cfg in self.LOOKUP_TABLES.items():
            df = pd.read_sql_query(
                f"SELECT {cfg['id']},{cfg['code']} FROM {cfg['table']}", conn
            )
            maps[name] = {r[cfg["code"]]: r[cfg["id"]] for _, r in df.iterrows()}

        return maps

    # --------------------------------------------------
    # PROCESSING
    # --------------------------------------------------

    def process_stats(self, maps):
        df = self._load_stats().copy()

        # Apply mappings
        df["AreaKey"] = df.areaID.replace("NA", -999).astype(int).replace(-999, None)
        df["Percentile"] = df["percentiles"].astype(float)
        for lookup_dict in self.LOOKUP_TABLES.values():
            df[lookup_dict["id"]] = (
                df[lookup_dict["src"]].astype(str).map(maps[lookup_dict["table"]])
            )

        # Pivot delta columns longer
        base = df[df.indicator_percentiles.notna()].copy()
        base["Value"] = base.indicator_percentiles
        base["Delta"] = False

        delta = df[df.delta_percentiles.notna()].copy()
        delta["Value"] = delta.delta_percentiles
        delta["Delta"] = True

        df = pd.concat([base, delta])

        # Output
        # Get list of column names and order from the existing table - use this to filter df
        cursor = self.conn.execute("PRAGMA table_info(EnsembleArealStatistics);")
        columns = cursor.fetchall()
        output_columns = [col[1] for col in columns if col[1] != "id"]
        df = df[output_columns]

        return list(df.itertuples(index=False, name=None))

    def process_members(self, maps):
        df = self._load_members().copy()

        # Apply mappings
        df["AreaKey"] = df.areaID.replace("NA", -999).astype(int).replace(-999, None)
        for lookup_dict in self.LOOKUP_TABLES.values():
            df[lookup_dict["id"]] = (
                df[lookup_dict["src"]].astype(str).map(maps[lookup_dict["table"]])
            )

        base = df[df.indicator.notna()].copy()
        base["Value"] = base.indicator
        base["Delta"] = False

        delta = df[df.delta.notna()].copy()
        delta["Value"] = delta.delta
        delta["Delta"] = True

        df = pd.concat([base, delta])

        # Output
        # Get list of column names and order from the existing table - use this to filter df
        cursor = self.conn.execute("PRAGMA table_info(MemberArealStatistics);")
        columns = cursor.fetchall()
        output_columns = [col[1] for col in columns if col[1] != "id"]
        df = df[output_columns]

        return list(df.itertuples(index=False, name=None))

    # --------------------------------------------------
    # INSERTS
    # --------------------------------------------------

    def import_stats(self):
        if self.ensemble_stats_csv is None:
            return

        rows = self.process_stats(self.build_mappings())
        conn = self.connect()
        conn.execute("PRAGMA foreign_keys=OFF;")
        cur = conn.cursor()

        # Data order is taken from the table, so no need to worry about specify the column names here
        cur.executemany(
            """
        INSERT INTO EnsembleArealStatistics
        VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?)
        """,
            rows,
        )

        conn.commit()
        conn.execute("PRAGMA foreign_keys=ON;")
        print("Inserted stats:", len(rows))

    def import_members(self):
        if self.member_stats_csv is None:
            return

        rows = self.process_members(self.build_mappings())
        conn = self.connect()
        conn.execute("PRAGMA foreign_keys=OFF;")
        cur = conn.cursor()

        # Data order is taken from the database table, so no need to worry about specify the column names here
        cur.executemany(
            """
        INSERT INTO MemberArealStatistics
        VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?)
        """,
            rows,
        )

        conn.commit()
        conn.execute("PRAGMA foreign_keys=ON;")
        print("Inserted members:", len(rows))

    def import_configuration(self):
        conn = self.connect()
        cur = conn.cursor()

        # Import configuration yaml
        cur.execute(
            """
        INSERT INTO Configuration 
        VALUES (NULL, 'config', ?,?)
        """,
            (self.config_file, json.dumps(self.config)),
        )

        # Loop over configuration tables
        for key, path in self.config["configuration_tables"].items():
            if (path is None) or (path == ""):
                continue
            # Load configuration table
            tbl = pd.read_csv(
                path,
                sep="\t",
                encoding="windows-1252",
                keep_default_na=False,
                dtype="str",
            )
            tbl = tbl[tbl["enabled"] != ""]
            cur.execute(
                """
            INSERT INTO Configuration 
            VALUES (NULL, ?, ?,?)
            """,
                (key, self.config["configuration_tables"][key], tbl.to_json()),
            )

        conn.commit()

    def register_gridded_files(self):
        conn = self.connect()
        cur = conn.cursor()

        # Get Filelists. Regridding may or may be included in the pipeline, and needs to be handled separate
        indicator_filelist = [
            k
            for thisInd in self.workflow["indicators"].values()
            for k in thisInd["outputs"]
        ]
        filelists = {
            "indicators": indicator_filelist,
            "ensstats": self.workflow["ensemble_statistics"]["outputs"],
        }
        if "outputs" in self.workflow["regrid"]:
            filelists["regrid"] = self.workflow["regrid"]["outputs"]

        # Build into a dataframe, and encode the pipeline step codes
        df = pd.DataFrame(
            [
                {"PipelineStep": code, "Path": path}
                for code, paths in filelists.items()
                for path in paths
            ]
        )
        df["PipelineStep"] = df["PipelineStep"].map(self.PIPELINE_STEPS)

        # Adjust the filepath to be relative to the SQLITE database and convert to str
        df["Path"] = [
            str(Path(p).relative_to(self.db_output_path.parent)) for p in df["Path"]
        ]

        # Now extract fields from the filename
        extracted = df[["Path"]].copy()
        extracted["filename"] = [Path(p).stem for p in extracted["Path"]]
        extract_column_names = [
            "Datasets",
            "Indicators",
            "Grids",
            "Scenarios",
            "Members",
        ]
        for i, n in enumerate(extract_column_names):
            extracted[n] = extracted["filename"].str.split("_").str[i]
        extracted["Members"] = (
            extracted["filename"].str.split("_").str[4:].str.join("_")
        )

        # Update grid mappings - in principle the source grids won't come through to the areal statistics and are therefore
        # not included in the original Grid mapping table. Add them to the Grids table and update the mapping.
        existing_grids = pd.read_sql_query("SELECT GridCode FROM Grids", conn)[
            "GridCode"
        ].tolist()
        new_grids = extracted["Grids"].unique()
        grids_to_add = [grid for grid in new_grids if grid not in existing_grids]
        if grids_to_add:
            rows = [
                (i + 1, grid)
                for i, grid in enumerate(grids_to_add, start=len(existing_grids))
            ]
            cur.executemany("INSERT INTO Grids (GridKey, GridCode) VALUES (?, ?)", rows)
            conn.commit()
            print(f"Added {len(grids_to_add)} new grids to the Grids table.")

        # Build mappings to convert codes to keys and write to df
        maps = self.build_mappings()
        for n in extract_column_names:
            lookup_dict = self.LOOKUP_TABLES[n]
            df[lookup_dict["id"]] = (
                extracted[n].astype(str).map(maps[lookup_dict["table"]])
            )

        # Ensure the DataFrame has the correct columns in the correct order
        # Retrieve the structure of the GriddedFiles table
        cur.execute("PRAGMA table_info(GriddedFiles);")
        table_info = cur.fetchall()
        table_columns = [col[1] for col in table_info if col[1] != "id"]
        out = df[table_columns]

        # Write to database
        conn.execute("PRAGMA foreign_keys=OFF;")
        cur = conn.cursor()

        # Data order is taken from the table, so no need to worry about specify the column names here
        cur.executemany(
            """
        INSERT INTO GriddedFiles
        VALUES (NULL,?,?,?,?,?,?,?)
        """,
            out.itertuples(index=False, name=None),
        )

        conn.commit()
        conn.execute("PRAGMA foreign_keys=ON;")
        print("Registered gridded files:", len(df))

    # --------------------------------------------------
    # INDEXES AND VIEWS
    # --------------------------------------------------

    def create_indexes_and_views(self):
        conn = self.connect()
        cur = conn.cursor()

        # -- Indexes on Ensemble_stats --
        if self.ensemble_stats_csv is not None:
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_stats_area        ON EnsembleArealStatistics(AreaKey);"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_stats_indicator   ON EnsembleArealStatistics(IndicatorKey);"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_stats_scenario    ON EnsembleArealStatistics(ScenarioKey);"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_stats_TimeBin      ON EnsembleArealStatistics(TimeBinKey);"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_stats_season      ON EnsembleArealStatistics(SeasonKey);"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_stats_grid        ON EnsembleArealStatistics(GridKey);"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_stats_dataset      ON EnsembleArealStatistics(DatasetKey);"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_stats_arealstat   ON EnsembleArealStatistics(StatisticTypeKey);"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_stats_delta       ON EnsembleArealStatistics(Delta);"
            )
            cur.execute(
                """
            CREATE INDEX IF NOT EXISTS idx_stats_composite
                ON EnsembleArealStatistics(IndicatorKey, ScenarioKey, TimeBinKey, SeasonKey, Delta);
            """
            )

        # -- Indexes on Ensemble_members --
        if self.member_stats_csv is not None:
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_mem_area          ON MemberArealStatistics(AreaKey);"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_mem_indicator     ON MemberArealStatistics(IndicatorKey);"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_mem_scenario      ON MemberArealStatistics(ScenarioKey);"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_mem_TimeBin        ON MemberArealStatistics(TimeBinKey);"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_mem_season        ON MemberArealStatistics(SeasonKey);"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_mem_dataset       ON MemberArealStatistics(DatasetKey);"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_mem_grid          ON MemberArealStatistics(GridKey);"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_mem_member        ON MemberArealStatistics(MemberKey);"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_mem_arealstat     ON MemberArealStatistics(StatisticTypeKey);"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_mem_delta         ON MemberArealStatistics(Delta);"
            )
            cur.execute(
                """
            CREATE INDEX IF NOT EXISTS idx_mem_composite
                ON MemberArealStatistics(IndicatorKey, ScenarioKey, TimeBinKey, SeasonKey, Delta);
            """
            )

        # -- View: Ensemble_stats with all metadata decoded --
        if self.ensemble_stats_csv is not None:
            cur.execute(
                """
            CREATE VIEW IF NOT EXISTS view_EnsembleArealStatistics AS
            SELECT
                es.id                   AS id,
                ds.DatasetCode          AS DatasetCode,
                sc.ScenarioCode         AS ScenarioCode,
                gr.GridCode             AS GridCode,
                i.IndicatorCode         AS IndicatorCode,
                i.IndicatorDescription  AS IndicatorDescription,
                es.AreaKey              AS AreaKey,
                p.TimeBinCode            AS TimeBinCode,
                p.TimeBinDescription     AS TimeBinDescription,
                se.SeasonCode           AS SeasonCode,
                se.SeasonDescription    AS SeasonDescription,
                ar.StatisticTypeCode   AS StatisticTypeCode,
                es.Delta                AS Delta,
                es.Percentile           AS Percentile,
                es.Value                AS Value
            FROM EnsembleArealStatistics AS es
            JOIN Indicators      AS i  ON es.IndicatorKey      = i.IndicatorKey
            JOIN Scenarios       AS sc ON es.ScenarioKey       = sc.ScenarioKey
            JOIN TimeBins        AS p  ON es.TimeBinKey         = p.TimeBinKey
            JOIN Seasons         AS se ON es.SeasonKey         = se.SeasonKey
            JOIN Grids           AS gr ON es.GridKey           = gr.GridKey
            JOIN Datasets        AS ds ON es.DatasetKey        = ds.DatasetKey
            JOIN StatisticTypes AS ar ON es.StatisticTypeKey = ar.StatisticTypeKey;
            """
            )

        # -- View: Ensemble_members with all metadata decoded --
        if self.member_stats_csv is not None:
            cur.execute(
                """
            CREATE VIEW IF NOT EXISTS view_MemberArealStatistics AS
            SELECT
                em.id                   AS id,
                ds.DatasetCode          AS DatasetCode,
                me.MemberCode           AS MemberCode,
                sc.ScenarioCode         AS ScenarioCode,
                gr.GridCode             AS GridCode,
                i.IndicatorCode         AS IndicatorCode,
                i.IndicatorDescription  AS IndicatorDescription,
                em.AreaKey              AS AreaKey,
                p.TimeBinCode            AS TimeBinCode,
                p.TimeBinDescription     AS TimeBinDescription,
                se.SeasonCode           AS SeasonCode,
                se.SeasonDescription    AS SeasonDescription,
                ar.StatisticTypeCode   AS StatisticTypeCode,
                em.Delta                AS Delta,
                em.Value                AS Value
            FROM MemberArealStatistics AS em
            JOIN Indicators      AS i  ON em.IndicatorKey      = i.IndicatorKey
            JOIN Scenarios       AS sc ON em.ScenarioKey       = sc.ScenarioKey
            JOIN TimeBins        AS p  ON em.TimeBinKey       = p.TimeBinKey
            JOIN Seasons         AS se ON em.SeasonKey         = se.SeasonKey
            JOIN Datasets        AS ds ON em.DatasetKey        = ds.DatasetKey
            JOIN Grids           AS gr ON em.GridKey           = gr.GridKey
            JOIN Members         AS me ON em.MemberKey         = me.MemberKey
            JOIN StatisticTypes AS ar ON em.StatisticTypeKey = ar.StatisticTypeKey;
            """
            )

        # -- View: Gridded files with all metadata decoded --
        cur.execute(
            """
        CREATE VIEW IF NOT EXISTS view_GriddedFiles AS
        SELECT
            gf.id                   AS id,
            ds.DatasetCode          AS DatasetCode,
            i.IndicatorCode         AS IndicatorCode,
            i.IndicatorDescription  AS IndicatorDescription,
            gr.GridCode             AS GridCode,
            me.MemberCode           AS MemberCode,
            sc.ScenarioCode         AS ScenarioCode,
            ps.PipelineStepKey     AS PipelineStepKey,
            ps.PipelineStepCode     AS PipelineStepCode,
            gf.Path                 AS Path
        FROM GriddedFiles AS gf
        JOIN Indicators      AS i  ON gf.IndicatorKey      = i.IndicatorKey
        JOIN Datasets        AS ds ON gf.DatasetKey        = ds.DatasetKey
        JOIN Grids           AS gr ON gf.GridKey           = gr.GridKey
        JOIN Scenarios       AS sc ON gf.ScenarioKey       = sc.ScenarioKey
        JOIN Members         AS me ON gf.MemberKey         = me.MemberKey
        JOIN PipelineSteps   AS ps ON gf.PipelineStep      = ps.PipelineStepKey;
        """
        )

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
            self.build_pipelineSteps_lookup()
            self.create_data_tables()
            self.import_descriptions()
            self.import_stats()
            self.import_members()
            self.import_configuration()
            self.register_gridded_files()
            self.create_indexes_and_views()
            print("\nSUCCESS")
        finally:
            self.close()

        # Move the result into place
        # Delete DB if it already exists
        if os.path.exists(self.db_output_path):
            os.remove(self.db_output_path)
        shutil.move(self.db_path, self.db_output_path)


# --------------------------------------------
# Example usage
# -------------------------------------------

if __name__ == "__main__":
    # Libraries
    from pathlib import Path
    import sys

    # Rely on the presence of .git to find the repo ROOT and
    # set as working directory
    ROOT = Path.cwd()
    while not (ROOT / ".git").exists():
        ROOT = ROOT.parent
    os.chdir(ROOT)

    # Setup for development
    sys.path.append(str(ROOT / "workflow"))

    # Set the path to configuration file
    configfile = ROOT / "config" / "config.yaml"
    configfile = ROOT / "workflow" / "testing" / "config.yaml"

    db = database(config_file=str(configfile), tempDir=tempfile.gettempdir())

    try:
        db.create_full_database()
    except ValueError as e:
        print(f"Validation Error: {e}")
    except FileNotFoundError as e:
        print(f"File Error: {e}")
    finally:
        db.close()
