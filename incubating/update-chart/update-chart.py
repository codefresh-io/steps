#!/usr/bin/env python3

""" DO NOT USE. While testing this script, I realized that becuae it always re-renders the YAML file, it always
    sorts the keys, which changes their order. This means that when you look at the commit for your updated YAML
    file in git, it will appear as though the entire file changed, as opposed to the one or two lines you actually
    intended to change. Unfortunately, I won't be able to use this script - switching to yq instead.

    Purpose:
    Accepts environment variables (arguments) from step.yaml as inputs. Applies the specified updates to
    Chart.yaml, and optionally values.yaml. Optionally increments the chart version. See step.yaml for
    explanation of all possible arguments.
"""

import os           # to read env vars
import yaml


def str_to_bool(bool_string):
    """ Convert a 'true' or 'false' string to a boolean.
    """
    assert bool_string.lower() in ['true', 'false'], "Value '{}' cannot be converted to boolean".format(bool_string)
    if bool_string.lower() == "true":
        return True
    return False


def list_to_dict(list_to_convert):
    """ Convert a list formatted like ['myAnnotation=someValue','otherAnnotation=otherValue'] into a
        dictionary formatted like {'myAnnotation': 'someValue', 'otherAnnotation': 'otherValue'}
    """
    dict = {}
    if not list_to_convert:
        return dict
    for element in list_to_convert:
        err_msg = "Unable to convert list element '{}' into a dictionary key:value pair. " + \
            "Required format is 'myAnnotation=someValue'"
        assert element.count("=") == 1, err_msg
        key_val = element.split('=')
        key = key_val[0]
        value = key_val[1]
        dict[key] = value
    return dict


def get_inputs_from_env_vars():
    """ Read environment variables. Format variables into lists and dictionaries to match their corresponding
        Chart.yaml structure. See step.yaml for full descriptions of environment variables. Also, since step.yaml
        is already enforcing which ones are mandatory, their data types, and default values, we don't do that here.
    """
    increment_chart_version = str_to_bool(os.environ.get("INCREMENT_CHART_VERSION"))
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
    dependency_match_alias = str_to_bool(os.environ.get("DEPENDENCY_MATCH_ALIAS"))
    dependency_name = os.environ.get("DEPENDENCY_NAME")
    dependency_tags_replace = str_to_bool(os.environ.get("DEPENDENCY_TAGS_REPLACE"))
    dependency_import_values_replace = str_to_bool(os.environ.get("DEPENDENCY_IMPORT_VALUES_REPLACE"))
    # Create a dict to store the 'dependencies' chart fields to update
    updated_dependency_fields={}
    if dependency_name:
        updated_dependency_fields['name'] = dependency_name
        dependency_version = os.environ.get("DEPENDENCY_VERSION")
        if dependency_version:
            updated_dependency_fields['version'] = dependency_version
        dependency_repository = os.environ.get("DEPENDENCY_REPOSITORY")
        if dependency_repository:
            updated_dependency_fields['repository'] = dependency_repository
        dependency_condition = os.environ.get("DEPENDENCY_CONDITION")
        if dependency_condition:
            updated_dependency_fields['condition'] = dependency_condition
        dependency_tags = os.environ.get("DEPENDENCY_TAGS")
        if dependency_tags:
            updated_dependency_fields['tags'] = dependency_tags.split(',')
        dependency_import_values = os.environ.get("DEPENDENCY_IMPORT_VALUES")
        if dependency_import_values:
            updated_dependency_fields['import-values'] = dependency_import_values.split(',')
        dependency_alias = os.environ.get("DEPENDENCY_ALIAS")
        if dependency_alias:
            updated_dependency_fields['alias'] = dependency_alias
    annotations_list = os.environ.get("ANNOTATIONS")
    annotations = list_to_dict(annotations_list)
    annotations_replace = str_to_bool(os.environ.get("ANNOTATIONS_REPLACE"))
    return increment_chart_version, values_to_update, fields_to_update, keywords, keywords_replace, sources, \
        sources_replace, updated_dependency_fields, dependency_match_alias, dependency_tags_replace, \
        dependency_import_values_replace, annotations, annotations_replace


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
    """ Take each "key=value" string in fields_to_update list, and apply them to chart_yaml as top-level key:value
        pairs. If 'version' isn't in the list, then increment the 'version' according to increment_chart_version bool.
    """
    if not fields_to_update:
        fields_to_update = []
    explicit_version = False
    for field_str in fields_to_update:
        key_value_pair = field_str.split('=')
        key = key_value_pair[0]
        value = key_value_pair[1]
        if key == "version":
            explicit_version = True
        chart_yaml[key] = value
    if (not explicit_version) and (increment_chart_version):
        chart_yaml['version'] = increment_version(chart_yaml['version'])


def update_list(chart_yaml, list_name, new_list, replace_flag):
    """ Add the elements from new_list to the specified list in chart_yaml. If replace_flag
        is True then don't bother appending them, just overwrite the whole list.
    """
    if not new_list:
        return
    # Overwrite if replace_flag, or if the list doesn't exist in chart_yaml yet
    if (replace_flag) or (list_name not in chart_yaml.keys()) or (not isinstance(chart_yaml[list_name], list)):
        chart_yaml[list_name] = new_list
    else:
        for element_to_add in new_list:
            # Don't add duplicate elements
            if element_to_add not in chart_yaml[list_name]:
                chart_yaml[list_name].append(element_to_add)


def get_dependency_by_name_and_alias(chart_yaml, chart_name, alias):
    """ Get a chart from the 'dependencies' list in chart_yaml by its name and alias. If the specified
        chart does not exist in the list, return None.
    """
    for dependency in chart_yaml['dependencies']:
        if 'name' in dependency.keys() and dependency['name'] == chart_name:
            if 'alias' in dependency.keys() and dependency['alias'] == alias:
                return dependency
    return None


def get_or_create_dependency_by_name(chart_yaml, chart_name):
    """ Get a chart from the 'dependencies' list in chart_yaml by its name. If it doesn't exist yet,
        then add a new chart to the list with that name, and return that.
    """
    if 'dependencies' not in chart_yaml.keys():
        chart_yaml['dependencies'] = []
    for dependency in chart_yaml['dependencies']:
        if 'name' in dependency.keys() and dependency['name'] == chart_name:
            return dependency
    new_dependency = { "name": chart_name }
    chart_yaml['dependencies'].append(new_dependency)
    return new_dependency


def update_dependency_list(chart_yaml, updated_dependency_fields, dependency_match_alias, 
                           dependency_tags_replace, dependency_import_values_replace):
    """ Updates a chart in chart_yaml's 'dependencies' list. The chart to update is specified by its 'name' and 
        optionally also its 'alias' depending on the dependency_match_alias bool param. When updating the chart, its 
        list fields can either be appended or replaced, depending on their bool params.
    """
    # ******** Stop now if there is nothing to do ********
    if not updated_dependency_fields:
        return
    # ******** Get the chart to update *********
    if 'dependencies' not in chart_yaml.keys():
        chart_yaml['dependencies'] = []
    chart_name = updated_dependency_fields['name']
    chart = None
    alias = None
    if 'alias' in updated_dependency_fields.keys():
        alias = updated_dependency_fields['alias']
    if alias and dependency_match_alias:
        chart = get_dependency_by_name_and_alias(chart_yaml, chart_name, alias)
    if not chart:
        chart = get_or_create_dependency_by_name(chart_yaml, chart_name)
    # ******** Copy updated fields into the chart *********
    for key in updated_dependency_fields.keys():
        # Append the 'tags' list if specified
        if key == 'tags' and not dependency_tags_replace:
            if 'tags' not in chart.keys():
                chart['tags'] = []
            for tag in updated_dependency_fields['tags']:
                # Don't add duplicate elements
                if tag not in chart['tags']:
                    chart['tags'].append(tag)
            continue
        # Append the 'import-values' list if specified
        if key == 'import-values' and not dependency_import_values_replace:
            if 'import-values' not in chart.keys():
                chart['import-values'] = []
            for import_value in updated_dependency_fields['import-values']:
                # Don't add duplicate elements
                if import_value not in chart['import-values']:
                    chart['import-values'].append(import_value)
            continue
        # Copy the field exactly / replace a whole list
        chart[key] = updated_dependency_fields[key]   


def update_annotations_dict(chart_yaml, annotations, annotations_replace):
    """ Add/update the key:value pairs from annotations to the 'annotations' dictionary in chart_yaml. If
        annotations_replace is True then don't bother add/updating them, just overwrite the whole dictionary.
    """
    if not annotations:
        return
    if annotations_replace:
        chart_yaml['annotations'] = annotations
    else:
        if 'annotations' not in chart_yaml.keys():
            chart_yaml['annotations'] = {}
        for annotation_key in annotations.keys():
            chart_yaml['annotations'][annotation_key] = annotations[annotation_key]


def update_dict_path(dict, dict_path_string, value):
    """ Traverses the specified path to a key within the dict, and sets it to the specified value.
        The format of dict_path_string is 'path.to.variable'. Does not work with lists.
    """
    if not dict_path_string:
        return
    path_hierarchy = dict_path_string.split('.')
    # set pointer to root of the dict
    hierarchy_pointer = dict
    num_levels = len(path_hierarchy) - 1
    i = 0
    # move the pointer down the hierarchy of the dict
    while i < num_levels:
        level = path_hierarchy[i]
        if level not in hierarchy_pointer.keys():
            hierarchy_pointer[level] = {}
        hierarchy_pointer = hierarchy_pointer[level]
        i += 1
    key = path_hierarchy[-1]
    try:
        hierarchy_pointer[key] = value
    except TypeError:
        msg = "Unable to apply value '{}' to path '{}'. The path might ".format(value, dict_path_string) + \
            "conflict with an existing, non-dictionary value in values.yaml: '{}'".format(hierarchy_pointer)
        raise TypeError(msg)


def update_values(values_yaml, values_to_update):
    """ Apply values_to_update (list of strings) as values within the values_yaml dictionary. The format
        of the strings is: path.to.key=value
    """
    for path_and_value in values_to_update:
        substrings = path_and_value.split('=')
        path = substrings[0]
        value = substrings[1]
        update_dict_path(values_yaml, path, value)


def main():
    # Get script args
    increment_chart_version, values_to_update, fields_to_update, keywords, keywords_replace, sources, \
         sources_replace, updated_dependency_fields, dependency_match_alias, dependency_tags_replace, \
         dependency_import_values_replace, annotations, annotations_replace = get_inputs_from_env_vars()

    # Update Chart.yaml
    with open("Chart.yaml", "r") as read_file:
        chart_yaml = yaml.load(read_file, Loader=yaml.SafeLoader)
    update_chart_fields(chart_yaml, increment_chart_version, fields_to_update)
    update_list(chart_yaml, 'keywords', keywords, keywords_replace)
    update_list(chart_yaml, 'sources', sources, sources_replace)
    update_dependency_list(chart_yaml, updated_dependency_fields, dependency_match_alias, 
                           dependency_tags_replace, dependency_import_values_replace)
    update_annotations_dict(chart_yaml, annotations, annotations_replace)
    # print(chart_yaml)
    with open("Chart.yaml", "w") as write_file:
        document = yaml.dump(chart_yaml, write_file)
   
    # Update values.yaml
    if values_to_update:
        with open("values.yaml", "r") as read_file:
            values_yaml = yaml.load(read_file, Loader=yaml.SafeLoader)
        if not values_yaml:
            values_yaml = {}
        update_values(values_yaml, values_to_update)
        # print(values_yaml)
        with open("values.yaml", "w") as write_file:
            document = yaml.dump(values_yaml, write_file)


if __name__ == "__main__":
    main()
