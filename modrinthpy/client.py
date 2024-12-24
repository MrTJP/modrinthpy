import requests
import json
import logging

logger = logging.getLogger("ModrinthClient")

class ModrinthClient:
    """
    ModrinthClient - This class exposes the raw Modrinth API.
    
    Specs: https://docs.modrinth.com/api/
    """

    def __init__(self, api_key):
        """
        Create a new api client. An optional API key (Personal Access Token) can be used to make calls that require authentication.
        
        
        To generate a token, go to user settings:
        https://modrinth.com/settings/account

        :param self: This object
        :param api_key: The personal access token. Can be empty.
        :return: The client
        """
        self._key = api_key
        self._base_url = 'https://api.modrinth.com'

    ### utlities
    def _get(self, endpoint, **kwargs):
        headers = {}
        if self._key:
            headers['Authorization'] = self._key
        try:
            response = requests.get(self._base_url + endpoint, headers=headers, **kwargs)
            # Raise an HTTPError for bad responses (4xx and 5xx)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error response: {response.json()}")
            raise e
    
    def _post(self, endpoint, **kwargs):
        headers = {}
        if self._key:
            headers['Authorization'] = self._key
        try:
            response = requests.post(self._base_url + endpoint, headers=headers, **kwargs)
            # Raise an HTTPError for bad responses (4xx and 5xx)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error response: {e.response.json()}")
            raise e
        
    def welcome(self):
        """
        Get the welcome message from the API
        """
        return self._get('/')
    
    ### projects api

    # TODO search

    def get_project(self, project_id: str):
        """
        Get a project by its ID: https://docs.modrinth.com/api/operations/getproject/

        :param project_id: The project ID or slug
        """
        endpoint = f'/v2/project/{project_id}'
        return self._get(endpoint)

    # TODO delete_project
    # TODO modify_project
    # TODO get_multiple_projects
    # TODO bulk_edit_projects
    # TODO get_random_projects
    # TODO create_project
    # TODO delete_project_icon
    # TODO change_project_icon
    # TODO check_project_slug_or_id
    # TODO add_gallery_image
    # TODO delete_gallery_image
    # TODO modify_gallery_image
    # TODO get_project_dependencies
    # TODO follow_project
    # TODO unfollow_project
    # TODO schedule_project

    ### versions api

    # TODO list_versions
    
    def get_version(self, version_id: str):
        """
        Get a version by its ID: https://docs.modrinth.com/api/operations/getversion/

        :param version_id: The version ID
        """
        endpoint = f'/v2/version/{version_id}'
        return self._get(endpoint)

    # TODO delete_version
    # TODO modify_version
    # TODO get_version_from_id
    # TODO create_version

    def create_version(self, 
                       name: str, 
                       version_num: str, 
                       change_log: str, 
                       deps: list[dict], 
                       game_versions: list[str], 
                       version_type: str, 
                       loaders: list[str], 
                       featured: bool, 
                       status: str, 
                       requested_status: str, 
                       project_id: str, 
                       file_paths: list[str]):
        """
        Create a new version for given project: https://docs.modrinth.com/api/operations/createversion/

        :param name: The name of the version
        :param version_num: The version number (semantic version for example)
        :param change_log: The changelog for the version (markdown string)
        :param deps: List of dependencies. Each dep is a dictionary with keys: 
                        version_id (optional): A depdenency version ID
                        project_id (optional): A dependency project ID
                        file_name (optional): A dependency file name, mostly used to specify an external dependency
                        dependency_type: Dependency type (required, optional, incompatible, embedded)
        :param game_versions: List of game versions the mod is compatible with
        :param version_type: The type of the version (alpha, beta, release)
        :param loaders: List of loaders the mod is compatible with (forge, neoforge, ...)
        :param featured: Whether the version is featured
        :param status: The status of the version (listed, archived, draft, unlisted, scheduled, unknown)
        :param requested_status: The requested status of the version (listed, archived, draft, unlisted)
        :param project_id: The project ID
        :param file_paths: List of file paths to upload. First one will be the primary file
        """
        endpoint = f'/v2/version'

        # The json body included in the multipart request
        data = {
            'name': name,
            'version_number': version_num,
            'changelog': change_log,
            'game_versions': game_versions,
            'version_type': version_type,
            'loaders': loaders,
            'featured': featured,
            'status': status,
            'requested_status': requested_status,
            'project_id': project_id,
            'file_parts': file_paths,
            'primary_file': file_paths[0]
        }
        if deps:
            data['dependencies'] = deps

        files = {
            'data': (None, json.dumps(data), 'application/json')
        }
        # Add each file
        for f in file_paths:
            files[f] = open(f, 'rb')

        # Post request
        response = self._post(endpoint, files=files)
        return response

    # TODO schedule_version
    # TODO get_multiple_versions
    # TODO add_files_to_version