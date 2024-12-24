"""
A command-line tool to expose some useful APIs from modrinthpy client
"""
import argparse
import logging
import os
from modrinthpy.client import ModrinthClient

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def parse_args():
    parser = argparse.ArgumentParser(
        prog='modrinthpy',
        description='Modrinth CLI',
        epilog='CLI for interacting with Modrinth')
    parser.add_argument(
        '--api-key', '-k',
        required=True,
        help='The Modrinth API key (PAT) to use for authentication')
    parser.add_argument(
        '--dryrun',
        action='store_true',
        help='Create the request but stop short of actually submitting it')
    
    subparsers = parser.add_subparsers(dest="command", help='A supported command')

    # New Version command
    new_ver = subparsers.add_parser('create-version', help='Create a new version for a project')
    new_ver.add_argument(
        '--name', '-n',
        required=True,
        help='A friendly name for the new version')
    new_ver.add_argument(
        '--version', '-v',
        help='Version string (semantic version, etc)')
    new_ver.add_argument(
        '--changelog-path', '-c',
        required=True,
        help='Path to a markdown file with changelog')
    new_ver.add_argument(
        '--embedded-dep', '-ed',
        action='append',
        help='Add an embedded library dependency (project id, project slug, or file name)')
    new_ver.add_argument(
        '--incompatible-dep', '-id',
        action='append',
        help='Add an incompatible dependency (project id, project slug, or file name)')
    new_ver.add_argument(
        '--optional-dep', '-od',
        action='append',
        help='Add an optional dependency (project id, project slug, or file name)')
    new_ver.add_argument(
        '--required-dep', '-rd',
        action='append',
        help='Add a required dependency (project id, project slug, or file name)')
    new_ver.add_argument(
        '--game-version', '-gv',
        required=True,
        action='append',
        help='Append a game version to associate the file with')
    new_ver.add_argument(
        '--version-type', '-vt',
        required=True,
        choices=['alpha', 'beta', 'release'],
        help='The release type of the file')
    new_ver.add_argument(
        '--loader', '-l',
        required=True,
        action='append',
        help='Append a loader for this version')
    parser.add_argument(
        '--featured', '-F',
        action='store_true',
        help='Mark this version as featured')
    parser.add_argument(
        '--status', '-s',
        choices=['listed', 'archived', 'draft', 'unlisted', 'scheduled', 'unknown'],
        default='listed',
        help='The initial status of the version')
    new_ver.add_argument(
        '--project', '-p',
        required=True,
        help='Project ID or slug to create the version for')
    new_ver.add_argument(
        '--file-path', '-f',
        required=True,
        action='append',
        help='Add a file to upload. First file added is marked as primary')

    # Parse
    args = parser.parse_args()

    # Check common arguments
    subcommands = ['create-version']
    if args.command not in subcommands:
        parser.error(f"Invalid command: {args.command}")
        return

    return args


def main():
    # Parse arguments
    args = parse_args()

    # Configure logging
    logger.setLevel(logging.DEBUG)

    # Create client
    client = ModrinthClient(args.api_key)

    # handle subcommand
    if args.command == "create-version":
        main_create_version(args, client)
        

def main_create_version(args, client: ModrinthClient):

    logger.info(f"Mapping project {args.project}")
    project_id = _resolve_project_id(client, args.project)

    if not project_id:
        logger.error(f"Project {args.project} not found")
        exit(1)

    logger.info(f"Mapped project {args.project} to {project_id}")

    # Map dependencies
    logger.info("Mapping dependencies")
    dependencies = []
    for ed in args.embedded_dep or []:
        dependencies.append(_resolve_dependency(client, ed, 'embedded'))
    for id in args.incompatible_dep or []:
        dependencies.append(_resolve_dependency(client, id, 'incompatible'))
    for od in args.optional_dep or []:
        dependencies.append(_resolve_dependency(client, od, 'optional'))
    for rd in args.required_dep or []:
        dependencies.append(_resolve_dependency(client, rd, 'required'))

    logger.info("Mapped dependencies: %s", dependencies)

    logger.info("Upload info:")
    logger.info(" - Project ID: %s", project_id)
    logger.info(" - Name: %s", args.name)
    logger.info(" - Version: %s", args.version)
    logger.info(" - Version Type: %s", args.version_type)
    logger.info(" - Changelog Path: %s", args.changelog_path)
    logger.info(" - Game Versions: %s", args.game_version)
    logger.info(" - Loaders: %s", args.loader)
    logger.info(" - Featured: %s", args.featured)
    logger.info(" - Dependencies: %s", dependencies)
    logger.info(" - Files: %s", args.file_path)
    
    # Read changelog
    with open(args.changelog_path, 'r') as f:
        changelog = f.read()

    logger.info("Calling create_version...")
    if args.dryrun:
        logger.info("Dry run mode enabled, skipping call")
        exit(0)

    # Upload version
    result = client.create_version(
        name=args.name,
        version_num=args.version,
        change_log=changelog,
        deps=dependencies,
        game_versions=args.game_version,
        version_type=args.version_type,
        loaders=args.loader,
        featured=args.featured,
        status=args.status,
        requested_status=args.status,
        project_id=project_id,
        file_paths=args.file_path
    )

    logger.info("Upload result: %s", result)
    

def _resolve_project_id(client, project):
    try:
        p = client.get_project(project)
        return p['id']
    except:
        return None

def _resolve_dependency(client, dep, dep_type):
    # Check if given id is a project id/slug
    try:
        p = client.get_project(dep)
        return {
            'project_id': p['id'],
            'dependency_type': dep_type
        }
    except:
        pass

    # Check if given id is a version id
    try:
        v = client.get_version(dep)
        return {
            'version_id': v['id'],
            'dependency_type': dep_type
        }
    except:
        pass

    # Must be a file name
    return {
        'file_name': dep,
        'dependency_type': dep_type
    }


if __name__ == '__main__':
    main()