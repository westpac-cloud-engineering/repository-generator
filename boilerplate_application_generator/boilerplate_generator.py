import os
import sys
import jinja2
import shutil

class JenkinsTemplate:
    def __init__(self, templates_path, template_name):
        self.template_path = os.path.join(templates_path, template_name, "jenkins")
        self.valid = self.validate_jenkins_structure()

    def validate_jenkins_structure(self):
        if os.path.isfile(os.path.join(self.template_path, "Jenkinsfile")):
            return True
        return False

    def generate_jenkins_configuration(self, destination_path):
        shutil.copy(os.path.join(self.template_path, "Jenkinsfile"), os.path.join(destination_path, "Jenkinsfile"))


class TerraformTemplate:
    def __init__(self, templates_path, template_name):
        self.template_path = os.path.join(templates_path, template_name, "terraform")
        self.template_name = template_name
        self.valid = self.validate_terraform_structure()
        self.j2_env = jinja2.Environment(loader=jinja2.PackageLoader('boilerplate_application_generator', 'templates'))

    def validate_terraform_structure(self):
        # Check that the three valid files, environment.tfvars, main.tf and variables.tf exists
        if not os.path.isfile(os.path.join(self.template_path, "environment.tfvars")):
            return False
        if not os.path.isfile(os.path.join(self.template_path, "main.tf")):
            return False
        if not os.path.isfile(os.path.join(self.template_path, "variables.tf")):
            return False
        return True

    def generate_terraform_configuration(self, destination_path, environments):
        print("Generating Terraform Configuration")
        template_directory = self.template_name + "/terraform/"

        # Generate Terraform Configuration Files
        tf_config_path = os.path.join(destination_path, "Terraform_Configuration")
        if not os.path.exists(tf_config_path):
            os.makedirs(tf_config_path)

        with open(os.path.join(tf_config_path, "main.tf"), "wb") as fh:
            fh.write(self.j2_env.get_template(template_directory + "main.tf").render().encode())
            print(' - Generating Terraform_Configuration/main.tf file')

        with open(os.path.join(tf_config_path, "variables.tf"), "wb") as fh:
            fh.write(self.j2_env.get_template(template_directory + "variables.tf").render().encode())
            print(' - Generating Terraform_Configuration/variables.tf file')

        # Generate Terraform Variables Files
        tf_vars_path = os.path.join(destination_path, "Terraform_Variables")
        if not os.path.exists(tf_vars_path):
            os.makedirs(tf_vars_path)

        for env in environments:
            with open(os.path.join(tf_vars_path, env + ".tfvars"), "wb") as fh:
                fh.write(self.j2_env.get_template(template_directory + "environment.tfvars").render().encode())
                print(' - Generating Terraform_Variables/' + env + '.variables.tf file')
        return False


class RepositoryTemplate:
    def __init__(self, template_name):
        self.template_name = template_name
        self.templates_path = os.path.join(sys.path[0], 'templates')
        self.template_path = os.path.join(self.templates_path, template_name)
        self.valid = self.validate_configuration_template()

        self.jenkins_template = JenkinsTemplate(self.templates_path, self.template_name)
        self.terraform_template = TerraformTemplate(self.templates_path, self.template_name)

    def validate_configuration_template(self):
        # TODO: More Robust Validation of Configuration Template
        if os.path.isfile(os.path.join(self.template_path, "definition.json")):
            return True
        else:
            return False

    def _generate_readme_contents(self):
        return False  # TODO: Generate README Contents

    def _generate_git_repository_and_upload(self):
        print("TODO: Convert to Git Repository and Upload")
        return False

    def generate_repository(self, target_directory, application_id, application_name, component_name, environments):

        repository_name = str(application_id + "_" + application_name + "_" + component_name).replace(" ", "-")
        target_directory = os.path.join(target_directory, repository_name)

        print("Generating repository based on template '" + self.template_name + "' in directory: \n" + target_directory + "\n")

        # Create Base folder
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)

        self._generate_readme_contents()

        # Generate Terraform Template
        if self.terraform_template.valid:
            self.terraform_template.generate_terraform_configuration(target_directory, environments)

        # Generate Jenkins Template
        if self.jenkins_template.valid:
            self.jenkins_template.generate_jenkins_configuration(target_directory)

        # Turn into a git repository and upload
        self._generate_git_repository_and_upload()


class GetAvailableRepositoryTemplates:
    def __init__(self):
        print("The available repository templates include:")
        for template_name in os.listdir(os.path.join(sys.path[0], 'templates')):
            template = RepositoryTemplate(template_name)

            if template.valid:
                print("- ", template.template_name)

        # self.generate_template_print('TEMPLATE_NAME_HERE')

    @staticmethod
    def generate_template_print(template):
        print("\nTo generate a template from this configuration, please run:")
        print("GenerateTemplate --template \"", template, "\" `")
        print("                 --directory \"DIRECTORY_TO_CREATE_REPOSITORY\" `")
        print("                 --app_name \"APPLICATION_NAME\" `")
        print("                 --component_name \"COMPONENT_NAME\" `")
        print("                 --environments Dev1 Test1 Test2 Etc")


# GetAvailableRepositoryTemplates()


rt = RepositoryTemplate('default')
rt.generate_repository(target_directory="C:\Repositories\deployments",
                       application_id="ABCD123",
                       application_name="My Awesome Application",
                       component_name='Infrastructure',
                       environments=['dev', 'test']
                       )
