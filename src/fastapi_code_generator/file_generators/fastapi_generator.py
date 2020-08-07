import os
import shutil
from os import mkdir

from mako.runtime import Context
from mako.template import Template
from requests import models

from fastapi_code_generator.schemas import baseschemas
from fastapi_code_generator.translators.json_translator import JsonTranslator


class FastApiGenerator:
    def gen_api_files(models, templates_path, target_path, project_name):
        project_dir = '{0}/src/{1}'.format(target_path, project_name)
        _mk_folder_structure(target_path, project_dir, models)

        for model in models:
            _gen_model_route_file(model, templates_path, target_path,
                                  project_name)
            _gen_model_domain_files(model, templates_path, target_path,
                                    project_name)
            _gen_model_test_files(model, templates_path, target_path,
                                  project_name)

        _gen_test_file(models, templates_path, target_path, project_name)
        _gen_common_project_files(models, templates_path, target_path,
                                  project_name)


def _gen_model_file(model, template_path, target_path, project_name):
    template = Template(filename=template_path)

    primary_key = _get_primary_key(model)

    content = template.render(
        model=model,
        PRIMARY_KEY_TYPE=JsonTranslator.translate_typename_to_pytypes(
            primary_key.type.name),
        PRIMARY_KEY_NAME=primary_key.name,
        PROJECT_NAME=project_name)

    with open(target_path, "w") as file:
        file.write(content)


def _gen_common_project_files(models, templates_path, target_path,
                              project_name):
    project_dir = '{0}/src/{1}'.format(target_path, project_name)

    template_service_factory_dir = '{0}/src/project/core/service_factory.py'.format(
        templates_path)
    service_factory_dir = '{0}/core/service_factory.py'.format(project_dir)

    _gen_file(template_service_factory_dir, service_factory_dir, project_name,
              models)

    template_base_schemas_dir = '{0}/src/project/domain/template_base_schemas.py'.format(
        templates_path)
    base_schemas_dir = '{0}/domain/base_schemas.py'.format(project_dir)

    _gen_file(template_base_schemas_dir, base_schemas_dir, project_name,
              models)

    template_project_init = '{0}/src/project/template_project_init.py'.format(
        templates_path)
    project_init = '{0}/__init__.py'.format(project_dir)

    _gen_file(template_project_init, project_init, project_name, models)


def _gen_test_file(models, templates_path, target_path, project_name):
    template_tests_util_dir = '{0}/tests/utils.py'.format(templates_path)
    tests_utils_dir = '{0}/tests/utils.py'.format(target_path)

    _gen_file(template_tests_util_dir, tests_utils_dir, project_name, models)

    template_conftest_dir = '{0}/tests/conftest.py'.format(templates_path)
    conftest_dir = '{0}/tests/conftest.py'.format(target_path)

    _gen_file(template_conftest_dir, conftest_dir, project_name, models)


def _gen_model_test_files(model, templates_path, target_path, project_name):
    template_tests_route_init_dir = '{0}/tests/test_route/__init__.py'.format(
        templates_path)
    tests_route_init_dir = '{0}/tests/test_{1}/__init__.py'.format(
        target_path, model.names.plural_name)

    _gen_model_file(model, template_tests_route_init_dir, tests_route_init_dir,
                    project_name)

    template_test_bp_dir = '{0}/tests/test_route/test_basic_positive.py'.format(
        templates_path)
    test_bp_dir = '{0}/tests/test_{1}/test_basic_positive.py'.format(
        target_path, model.names.plural_name)

    _gen_model_file(model, template_test_bp_dir, test_bp_dir, project_name)

    template_test_iin_dir = '{0}/tests/test_route/test_invalid_input_negative.py'.format(
        templates_path)
    test_iin_dir = '{0}/tests/test_{1}/test_invalid_input_negative.py'.format(
        target_path, model.names.plural_name)

    _gen_model_file(model, template_test_iin_dir, test_iin_dir, project_name)

    template_test_vin_dir = '{0}/tests/test_route/test_valid_input_negative.py'.format(
        templates_path)
    test_vin_dir = '{0}/tests/test_{1}/test_valid_input_negative.py'.format(
        target_path, model.names.plural_name)

    _gen_model_file(model, template_test_vin_dir, test_vin_dir, project_name)

    template_test_ep_dir = '{0}/tests/test_route/test_extended_positive.py'.format(
        templates_path)
    test_ep_dir = '{0}/tests/test_{1}/test_extended_positive.py'.format(
        target_path, model.names.plural_name)

    _gen_model_file(model, template_test_ep_dir, test_ep_dir, project_name)

    template_test_dest_dir = '{0}/tests/test_route/test_destructive.py'.format(
        templates_path)
    test_dest_dir = '{0}/tests/test_{1}/test_destructive.py'.format(
        target_path, model.names.plural_name)

    _gen_model_file(model, template_test_dest_dir, test_dest_dir, project_name)


def _gen_model_route_file(model, templates_path, target_path, project_name):
    project_dir = '{0}/src/{1}'.format(target_path, project_name)

    template_routers_dir = '{0}/src/project/routers/template_route.py'.format(
        templates_path)

    routers_dir = '{0}/routers/{1}_route.py'.format(
        project_dir,
        model.names.plural_name,
    )

    _gen_model_file(model, template_routers_dir, routers_dir, project_name)


def _gen_model_domain_files(model, templates_path, target_path, project_name):
    project_dir = '{0}/src/{1}'.format(target_path, project_name)

    template_services_dir = '{0}/src/project/domain/model/template_services.py'.format(
        templates_path)

    services_dir = '{0}/domain/{1}/{2}_services.py'.format(
        project_dir,
        model.names.plural_name,
        model.names.singular_name,
    )

    _gen_model_file(model, template_services_dir, services_dir, project_name)

    template_queries_dir = '{0}/src/project/domain/model/template_queries.py'.format(
        templates_path)

    queries_dir = ('{0}/domain/{1}/{2}_queries.py'.format(
        project_dir,
        model.names.plural_name,
        model.names.singular_name,
    ))

    _gen_model_file(model, template_queries_dir, queries_dir, project_name)

    template_model_dir = '{0}/src/project/domain/model/template_model.py'.format(
        templates_path)

    model_dir = '{0}/domain/{1}/{2}_model.py'.format(
        project_dir,
        model.names.plural_name,
        model.names.singular_name,
    )

    _gen_model_file(model, template_model_dir, model_dir, project_name)

    template_schemas_dir = '{0}/src/project/domain/model/template_schemas.py'.format(
        templates_path)

    schemas_dir = ('{0}/domain/{1}/{2}_schemas.py'.format(
        project_dir,
        model.names.plural_name,
        model.names.singular_name,
    ))

    _gen_model_file(model, template_schemas_dir, schemas_dir, project_name)


def _gen_file(template_path, target_path, project_name, models):
    template = Template(filename=template_path)

    content = template.render(PROJECT_NAME=project_name, models=models)

    with open(target_path, "w") as file:
        file.write(content)


def _get_primary_key(model: baseschemas.Model):
    """get_primary_key.

    Args:
        table (sql_column_parser.schemas.Table): [description]

    Returns:
        [type]: [description]
    """
    possible_keys = []
    preferred_types = ['uuid', 'interger']
    for field in model.fields:
        if field.is_primary_key:
            if field.type.name in preferred_types:
                return field
            else:
                possible_keys.append(field)

    return possible_keys[0]


def _mk_folder_structure(target_path, project_dir, models):
    """mk_folder_structure.

        Args:
            target_path ([type]): [description]
            project_dir ([type]): [description]
            plural_name ([type]): [description]
        """
    _mk_dir(
        '{0}/src'.format(target_path),
        project_dir,
        '{0}/core'.format(project_dir),
        '{0}/domain'.format(project_dir),
        '{0}/routers'.format(project_dir),
        '{0}/tests'.format(target_path),
    )

    for model in models:
        _mk_dir(
            '{0}/domain/{1}'.format(project_dir, model.names.plural_name),
            '{0}/tests/test_{1}'.format(target_path, model.names.plural_name),
        )


def _mk_dir(*target_paths):
    """mk_dir.

        Args:
            target_path ([type]): [description]
        """
    for target_path in target_paths:
        if not os.path.exists(target_path):
            try:
                print('Created folder at: {0}'.format(target_path))
                os.mkdir(target_path)
            except OSError:
                return
        else:
            print(
                'Folder at: {0} already exists. Using existing folder instead.'
                .format(target_path))
