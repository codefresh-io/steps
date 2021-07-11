#!/usr/bin/env python3

""" Purpose:
        
    Required environment variables:
      - 
    Optional environment variables:
      - 
    Output files:
      - 
"""

import os           # to read env vars
import yaml


def str_to_bool(bool_string):
    assert bool_string.lower() in ['true', 'false'], "Value '{}' cannot be converted to boolean".format(bool_string)
    if bool_string.lower() == "true":
        return True
    return False

def get_inputs_from_env_vars():
    """ Read environment variables. Format variables into lists and dictionaries to match the corresponding
        Chart.yaml structure.
    """
    increment_chart_version = os.environ.get("INCREMENT_CHART_VERSION")
    values_to_update = os.environ.get("VALUES_TO_UPDATE")
    if values_to_update:
        values_to_update = values_to_update.split(',')
    fields_to_update = os.environ.get("FIELDS_TO_UPDATE")
    if fields_to_update:
        fields_to_update = fields_to_update.split(',')
    keywords = os.environ.get("KEYWORDS")
    if keywords:
        keywords = keywords.split(',')
    keywords_replace = str_to_bool(os.environ.get("KEYWORDS_REPLACE"))
    sources = os.environ.get("SOURCES")
    if sources:
        sources = sources.split(',')
    sources_replace = str_to_bool(os.environ.get("SOURCES_REPLACE"))
    dependency_replace = str_to_bool(os.environ.get("DEPENDENCY_REPLACE"))
    dependency_name = os.environ.get("DEPENDENCY_NAME")
    # Create a dict to store 'dependencies' entries to update
    dependency_chart={}
    if dependency_name:
        dependency_chart['name'] = dependency_name
        dependency_version = os.environ.get("DEPENDENCY_VERSION")
        if dependency_version:
            dependency_chart['version'] = dependency_version
        dependency_repository = os.environ.get("DEPENDENCY_REPOSITORY")
        if dependency_repository:
            dependency_chart['repository'] = dependency_repository
        dependency_condition = os.environ.get("DEPENDENCY_CONDITION")
        if dependency_condition:
            dependency_chart['condition'] = dependency_condition
        dependency_tags = os.environ.get("DEPENDENCY_TAGS")
        if dependency_tags:
            dependency_chart['tags'] = dependency_tags.split(',')
        dependency_tags_replace = str_to_bool(os.environ.get("DEPENDENCY_TAGS_REPLACE"))
        dependency_import_values = os.environ.get("DEPENDENCY_IMPORT_VALUES")
        if dependency_import_values:
            dependency_chart['import-values'] = dependency_import_values.split(',')
        dependency_import_values_replace = str_to_bool(os.environ.get("DEPENDENCY_IMPORT_VALUES_REPLACE"))
        dependency_alias = os.environ.get("DEPENDENCY_ALIAS")
        if dependency_alias:
            dependency_chart['alias'] = dependency_alias
    annotations = os.environ.get("ANNOTATIONS")
    annotations_replace = str_to_bool(os.environ.get("ANNOTATIONS_REPLACE"))
    return increment_chart_version, values_to_update, fields_to_update, keywords, keywords_replace, sources, sources_replace, \
        dependency_chart, dependency_tags_replace, dependency_import_values_replace, annotations, annotations_replace


def increment_version(version):
    """ Increment the last digit of the specified semver.
    """
    semver_array = version.split('.')
    last_digit = int(semver_array[-1]) + 1
    semver_array[-1] = str(last_digit)
    new_version = ""
    digit_count = 0
    for digit in semver_array:
        if digit_count != 0:
            new_version += "."
        new_version += str(digit)
        digit_count += 1
    return new_version


def update_chart_fields(chart_yaml, increment_chart_version, fields_to_update):
    """ Take each "key=value" string in fields_to_update list, and apply it to chart_yaml dict. If a
        'version' wasn't provided, then increment the 'version' based on increment_chart_version bool.
    """
    explicit_version = False
    for field_str in fields_to_update:
        key_value_pair = field_str.split('=')
        key = key_value_pair[0]
        value = key_value_pair[1]
        if key == "version":
            explicit_version = True
        chart_yaml[key] = value
    if not explicit_version and increment_chart_version:
        chart_yaml['version'] = increment_version(chart_yaml['version'])


def update_keywords_list(chart_yaml, keywords, keywords_replace):
    pass


def update_sources_list(chart_yaml, sources, sources_replace):
    pass


def update_dependency_list(chart_yaml, dependency_chart, dependency_tags_replace, dependency_import_values_replace):
    pass


def update_annotations_dict(chart_yaml, annotations, annotations_replace):
    pass


def update_values(values_yaml, values_to_update):
    pass


def main():
    # Get script args
    increment_chart_version, values_to_update, fields_to_update, keywords, keywords_replace, sources, sources_replace, dependency_chart, \
        dependency_tags_replace, dependency_import_values_replace, annotations, annotations_replace = get_inputs_from_env_vars()
    
    # Read source YAML files
    with open("Chart.yaml", "r") as read_file:
        chart_yaml = yaml.load(read_file, Loader=yaml.SafeLoader)
    with open("values.yaml", "r") as read_file:
        values_yaml = yaml.load(read_file, Loader=yaml.SafeLoader)

    # Update chart_yaml
    update_chart_fields(chart_yaml, increment_chart_version, fields_to_update)
    update_keywords_list(chart_yaml, keywords, keywords_replace)
    update_sources_list(chart_yaml, sources, sources_replace)
    update_dependency_list(chart_yaml, dependency_chart, dependency_tags_replace, dependency_import_values_replace)
    update_annotations_dict(chart_yaml, annotations, annotations_replace)
   
    # Update values_yaml
    update_values(values_yaml, values_to_update)


if __name__ == "__main__":
    main()
