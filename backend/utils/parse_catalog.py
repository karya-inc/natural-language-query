from dataclasses import dataclass
import json
from typing import Any, List
from jsonschema import exceptions, Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012
from rbac.check_permissions import RoleTablePrivileges
from executor.catalog import Catalog
from utils.logger import get_logger

logger = get_logger("[CATALOG]")

# Get all the json schema files and setup Registry
catalogs_schema = {}
with open("catalogs.schema.json", "r") as f:
    catalogs_schema = json.load(f)

roles_schema = {}
with open("roles.schema.json", "r") as f:
    roles_schema = json.load(f)


schema_registry = Registry().with_resources(
    [
        (
            catalogs_schema["$id"],
            Resource.from_contents(catalogs_schema, DRAFT202012),
        ),
        (roles_schema["$id"], Resource.from_contents(roles_schema, DRAFT202012)),
    ]
)


catalogs_validator = Draft202012Validator(catalogs_schema, registry=schema_registry)
roles_validator = Draft202012Validator(roles_schema, registry=schema_registry)

TablePrivilagesMap = dict[str, List[RoleTablePrivileges]]


@dataclass
class ParsedCatalogConfiguration:
    catalogs: List[Catalog]
    database_privileges: dict[str, TablePrivilagesMap]


def parse_catalog_configuration() -> ParsedCatalogConfiguration:
    """
    Parse the database schema and permission info from the catalogs.json file

    Returns: ParsedCatalogConfiguration, containing the parsed catalogs and database privileges

    """
    # Load the catalog definitions
    with open("catalogs.json", "r") as f:
        catalog_defs: dict[str, Any] = json.load(f)

    # Validate the database schema
    try:
        catalogs_validator.validate(instance=catalog_defs)
    except exceptions.ValidationError as e:
        logger.error(f"Error validating database schema. Message: {e}")

    # Parse the database schema
    databases: dict[str, dict] = catalog_defs["databases"]

    catalogs: List[Catalog] = []
    database_privileges: dict[str, TablePrivilagesMap] = {}
    for dbname, dbinfo in databases.items():
        logger.info(f"Parsing Database: {dbname}")
        catalogs.append(
            Catalog(
                name=dbname,
                provider=dbinfo["connection"]["provider"],
                schema=dbinfo["tables"],
                connection_params=dbinfo["connection"],
            )
        )

        table_permisions: TablePrivilagesMap = {}
        for tablename, table in dbinfo["tables"].items():
            logger.info(f"Table: {tablename}")

            table_permisions[tablename] = []
            for permission in table["permissions"]:
                logger.info(f"Parsing Permission: {permission} for table {tablename}")

                table_permisions[tablename].append(
                    RoleTablePrivileges(
                        role_id=permission["role"],
                        table=tablename,
                        columns=permission["allowedColumns"],
                        scoped_columns=permission.get("scopes", []),
                    )
                )

            database_privileges[dbname] = table_permisions

    return ParsedCatalogConfiguration(
        catalogs=catalogs, database_privileges=database_privileges
    )


parsed_catalogs = parse_catalog_configuration()
