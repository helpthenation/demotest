from odoo import api, models
import xlrd
import xlsxwriter
from datetime import datetime
import logging
from datetime import date

_logger = logging.getLogger(__name__)


class ExportDataViews(models.Model):
    _name = 'export.data.views'

    def export_views(self):
        """
        Author:Bhavesh Jadav TechUltra Solutions
        Date:28/08/2020
        Func:This method use for the generate xls file from the cron of the table data
        :return: True
        """
        data_dict = {}
        table_data_list = self.get_employee_data_list()
        data_dict.update({'V_MASTER_EMPLOYEE': table_data_list})
        table_data_list = self.get_hrjob_data_list()
        data_dict.update({'V_MASTER_JOB': table_data_list})
        table_data_list = self.get_jobgrade_data_list()
        data_dict.update({'V_MASTER_GRADE': table_data_list})
        table_data_list = self.get_emp_contacts()
        data_dict.update({'V_EMP_CONTACTS': table_data_list})
        table_data_list = self.get_hr_compensation()
        data_dict.update({'V_EMP_COMPENSATION': table_data_list})
        table_data_list = self.get_hr_department()
        data_dict.update({'V_MASTER_ORG': table_data_list})
        table_data_list = self.get_emp_dependents()
        data_dict.update({'V_EMP_DEPENDENTS': table_data_list})
        table_data_list = self.get_emp_education()
        data_dict.update({'V_EMP_EDUCATION': table_data_list})
        table_data_list = self.get_emp_previous_employments()
        data_dict.update({'V_EMP_PREVIOUS_EMPLOYMENTS': table_data_list})
        # table_data_list = self.get_planned_vacancies()
        # data_dict.update({'V_ALL_PLANNED_VACANCIES': table_data_list})
        table_data_list = self.get_all_recruitment_details()
        data_dict.update({'V_ALL_RECRUITMENT_DETAILS': table_data_list})
        table_data_list = self.get_emp_performance()
        data_dict.update({'V_EMP_PERFORMANCE': table_data_list})
        table_data_list = self.get_emp_termination()
        data_dict.update({'V_EMP_TERMINATIONS': table_data_list})
        table_data_list = self.get_master_location()
        data_dict.update({'V_MASTER_LOCATION': table_data_list})
        table_data_list = self.get_emp_assignments()
        data_dict.update({'V_EMP_ASSIGNMENTS': table_data_list})
        if data_dict:
            self.generate_xls(data_dict)
        return True

    def generate_xls(self, data_dict):
        """
        Author: Bhavesh Jadav TechUltra Solutions
        Date:31/08/2020
        Func: this method use for the generate xls file of the each table from the key of the data_dict
        :param data_dict:use for the list of the dictionary for the generate xls file from the dict data
        :return: True
        """
        table_names = data_dict.keys()
        select_type = self.env['ir.config_parameter'].sudo()
        xls_cron_path = select_type.get_param('res.config.settings.xls_cron_path')
        if xls_cron_path:
            if xls_cron_path.endswith('\\') or xls_cron_path.endswith('/'):
                filepath = xls_cron_path
            else:
                separator = ''
                if '\\' in xls_cron_path:
                    separator = '\\'
                elif '/' in xls_cron_path:
                    separator = '/'
                filepath = xls_cron_path + separator
        else:
            filepath = '/tmp/'

        for table_name in table_names:
            # write xls
            filename = str(table_name) + '.xlsx'
            workbook = xlsxwriter.Workbook(filepath + filename)
            cell_text_format = workbook.add_format({'align': 'left', 'bold': True, 'size': 12})
            info_format = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'bold': True, 'size': 14})
            worksheet = workbook.add_worksheet(table_name)

            # set column size
            worksheet.set_column(0, 70, 30)

            row = 1
            for data in data_dict.get(table_name):
                headers = data.keys()
                col = 0
                for header in headers:
                    if row == 1:
                        worksheet.write(0, col, header, cell_text_format)
                    try:
                        worksheet.write(row, col, data.get(header))
                    except:
                        _logger.info('there is a issue in write xls data: %d ', data.get(header))
                        continue
                    col += 1
                row += 1
            if not data_dict.get(table_name):
                worksheet.merge_range('A1:C2', 'The record was  not found for that table please verify the data ',
                                      info_format)
            workbook.close()
        return True

    def get_employee_data_list(self):
        """
        Author:Bhavesh Jadav TechUltra Solutions
        Date:28/08/2020
        Func: this method use for the prepare list of dictionary for the xls file from the hr.employee
        :return: V_MASTER_EMPLOYEE_data_list: list of dictionary the xls file
        """
        V_MASTER_EMPLOYEE_data_list = []
        hr_employee_obj = self.env['hr.employee']
        employee_ids = hr_employee_obj.search([])
        for employee_id in employee_ids:
            data_dict = {}
            passport_id = False
            visa_id = False
            emirates_id = False
            family_book_id = False
            document_type_family_book = self.env['document.types'].search([('name', '=', 'Family Book')], limit=1)
            document_type_emirates = self.env['document.types'].search([('name', '=', 'Emirates ID')], limit=1)
            document_type_passport = self.env['document.types'].search([('name', '=', 'Passport')], limit=1)
            document_type_visa = self.env['document.types'].search([('name', '=', 'Visa')], limit=1)
            if document_type_passport:
                passport_id = self.env['documents.document'].search(
                    [('res_id', '=', employee_id.id), ('res_model', '=', 'hr.employee'),
                     ('document_type_id', '=', document_type_passport.id)], limit=1, order='desc')
            if document_type_visa:
                visa_id = self.env['documents.document'].search(
                    [('res_id', '=', employee_id.id), ('res_model', '=', 'hr.employee'),
                     ('document_type_id', '=', document_type_visa.id)], limit=1, order='desc')
            if document_type_emirates:
                emirates_id = self.env['documents.document'].search(
                    [('res_id', '=', employee_id.id), ('res_model', '=', 'hr.employee'),
                     ('document_type_id', '=', document_type_emirates.id)], limit=1, order='desc')
            if document_type_family_book:
                family_book_id = self.env['documents.document'].search(
                    [('res_id', '=', employee_id.id), ('res_model', '=', 'hr.employee'),
                     ('document_type_id', '=', document_type_family_book.id)], limit=1, order='desc')

            # passport_id = employee_id.own_document_o2m.filtered(lambda id: id.document_type_id.name == 'Passport')
            # visa_id = employee_id.own_document_o2m.filtered(lambda id: id.document_type_id.name == 'Visa')
            EMPLOYEE_ID = employee_id.system_id or ''
            CONTINGENT_WORKER_ID = ''
            EMIRATES_ID = emirates_id and emirates_id.emirates_id or ''
            ABSHER_FLAG = employee_id.absher_flag or ''
            FAMILY_BOOK_ID = family_book_id and family_book_id.family_book or ''
            PENSION_ID_NUMBER = employee_id.pension_id_number or ''
            UNIFIED_NUMBER = passport_id and passport_id.passport_unified_no or ''
            TAWTEEN_NUMBER = ''
            EMP_PASSPORT_TYPE = ''
            EMP_PASSPORT_NUMBER = passport_id and passport_id.passport_no or ''
            EMP_PASSPORT_ISSUE_DT = passport_id and passport_id.issue_date and passport_id.issue_date.strftime(
                "%d/%m/%Y") or ''
            EMP_PASSPORT_EXPIRY_DT = passport_id and passport_id.expiry_date and passport_id.expiry_date.strftime(
                "%d/%m/%Y") or ''
            EMP_PASSPORT_PLACE_OF_ISSUE = passport_id and passport_id.passport_place_issue or ''
            EMP_PASSPORT_CUONTRY_OF_ISSUE = passport_id and passport_id.passport_country_issue and passport_id.passport_country_issue.name or ''
            PERM_RES_ADDRESS_LINE1 = employee_id.street or ''
            PERM_RES_ADDRESS_LINE2 = employee_id.street or ''
            PERM_RES_BUILDING_OR_VILLA_NO = ''
            PERM_RES_STREET = employee_id.street or ''
            PERM_RES_CITY = employee_id.state_id and employee_id.state_id.name or ''
            PERM_RES_STATE = employee_id.state_id and employee_id.state_id.name or ''
            PERM_RES_ZIP_CODE = ''
            PERM_RES_COUNTRY = employee_id.country_id and employee_id.country_id.name or ''
            EMP_MARITAL_STATUS = employee_id.marital or ''
            EMP_RELIGION = employee_id.religion or ''
            EMP_DATE_OF_BIRTH = employee_id.birthday and employee_id.birthday.strftime("%d/%m/%Y") or ''
            EMP_PLACE_OF_BIRTH = employee_id.place_of_birth or ''
            EMP_COUNTRY_OF_BIRTH = employee_id.country_of_birth and employee_id.country_of_birth.name or ''
            EMP_NATIONALITY = employee_id.country_id and employee_id.country_id.name or ''
            EMP_GENDER = employee_id.gender or ''
            EMP_PHYSICAL_DISABILITY_FLAG = ''
            EMP_MILITARY_SERVICE_START_DT = employee_id.emp_military_service_start_date or ''
            EMP_MILITARY_SERVICE_END_DT = employee_id.emp_military_service_end_date or ''
            EMP_MILITARY_SERVICE_TITLE = employee_id.emp_military_service_title or ''
            EMP_MILITARY_SERVICE_COUNTRY = employee_id.emp_military_service_country or ''
            EMP_PICTURE = employee_id.image_1920 and str(employee_id.image_1920) or ''
            EMP_MOBILE_NUMBER = employee_id.mobile_phone or ''
            EMP_EMAIL_ID = employee_id.private_email or ''
            EMP_OFFICE_LOCATION = employee_id.work_location or ''
            EMP_OFFICE_PHONE_NUMBER = employee_id.work_phone or ''
            EMP_TITLE = employee_id.title and employee_id.title.name or ''
            EMP_FIRST_NAME = employee_id.firstname or ''
            EMP_ARABIC_FATHER_NAME = ''
            EMP_ARABIC_MOTHER_NAME = employee_id.arabic_mothers_name or ''
            EMP_MIDDLE_NAME = employee_id.middlename or ''
            EMP_PARENTAL_GRANDFATHERS_NAME = ''
            EMP_FAMILY_NAME = str(employee_id.lastname) or ''
            EMP_FULL_NAME = str(employee_id.firstname) + ' ' + str(employee_id.middlename) + ' ' + str(
                employee_id.lastname)
            EMP_PREFERRED_NAME = ''
            EMP_FATHERS_NAME = ''
            EMP_MOTHERS_NAME = employee_id.mothers_name or ''
            EMP_ARABIC_FULL_NAME = employee_id.arabic_name or ''
            EMP_ARABIC_LAST_NAME = ''
            EMP_UAE_ADD_BUILDING_OR_VILLA = ''
            EMP_UAE_ADD_STREET = ''
            EMP_UAE_ADD_CITY = ''
            EMP_UAE_ADD_EMIRATE = ''
            EMP_UAE_ADD_RESIDENTIAL_TYPE = ''
            START_DATE = employee_id.resume_line_ids and employee_id.resume_line_ids[0].date_start and \
                         employee_id.resume_line_ids[0].date_start.strftime("%d/%m/%Y") or ''
            END_DATE = employee_id.resume_line_ids and employee_id.resume_line_ids[0].date_end and \
                       employee_id.resume_line_ids[0].date_end.strftime("%d/%m/%Y") or ''
            EMP_UAE_ADD_RENTAL_VALUE = ''
            EMP_UAE_ADD_TAWTHEEQ_NO = ''
            EMP_VISA_NUMBER = visa_id and visa_id.visa_file_no or ''
            EMP_VISA_ISSUE_DT = visa_id and visa_id.issue_date and visa_id.issue_date.strftime("%d/%m/%Y") or ''
            EMP_VISA_EXPIRY_DT = visa_id and visa_id.expiry_date and visa_id.expiry_date.strftime("%d/%m/%Y") or ''
            EMP_VISA_PLACE_OF_ISSUE = visa_id and visa_id.visa_place_issue or ''
            EMP_VISA_COMPANY_SPONSORED_FLG = ''
            EMP_VISA_SPONSOR_NAME = visa_id and visa_id.visa_sponsor or ''
            EMP_VISA_SPONSOR_CONTACT = ''
            EMP_VISA_TITLE_ENGLISH = ''
            EMP_VISA_TITLE_ARABIC = ''
            data_dict.update({'EMPLOYEE_ID': EMPLOYEE_ID,
                              'CONTINGENT_WORKER_ID': CONTINGENT_WORKER_ID,
                              'EMIRATES_ID': EMIRATES_ID,
                              'ABSHER_FLAG': ABSHER_FLAG,
                              'FAMILY_BOOK_ID': FAMILY_BOOK_ID,
                              'PENSION_ID_NUMBER': PENSION_ID_NUMBER,
                              'UNIFIED_NUMBER': UNIFIED_NUMBER,
                              'TAWTEEN_NUMBER': TAWTEEN_NUMBER,
                              'EMP_PASSPORT_TYPE': EMP_PASSPORT_TYPE,
                              'EMP_PASSPORT_NUMBER': EMP_PASSPORT_NUMBER,
                              'EMP_PASSPORT_ISSUE_DT': EMP_PASSPORT_ISSUE_DT,
                              'EMP_PASSPORT_EXPIRY_DT': EMP_PASSPORT_EXPIRY_DT,
                              'EMP_PASSPORT_PLACE_OF_ISSUE': EMP_PASSPORT_PLACE_OF_ISSUE,
                              'EMP_PASSPORT_CUONTRY_OF_ISSUE': EMP_PASSPORT_CUONTRY_OF_ISSUE,
                              'PERM_RES_ADDRESS_LINE1': PERM_RES_ADDRESS_LINE1,
                              'PERM_RES_ADDRESS_LINE2': PERM_RES_ADDRESS_LINE2,
                              'PERM_RES_BUILDING_OR_VILLA_NO': PERM_RES_BUILDING_OR_VILLA_NO,
                              'PERM_RES_STREET': PERM_RES_STREET,
                              'PERM_RES_CITY': PERM_RES_CITY,
                              'PERM_RES_STATE': PERM_RES_STATE,
                              'PERM_RES_ZIP_CODE': PERM_RES_ZIP_CODE,
                              'PERM_RES_COUNTRY': PERM_RES_COUNTRY,
                              'EMP_MARITAL_STATUS': EMP_MARITAL_STATUS,
                              'EMP_RELIGION': EMP_RELIGION,
                              'EMP_DATE_OF_BIRTH': EMP_DATE_OF_BIRTH,
                              'EMP_PLACE_OF_BIRTH': EMP_PLACE_OF_BIRTH,
                              'EMP_COUNTRY_OF_BIRTH': EMP_COUNTRY_OF_BIRTH,
                              'EMP_NATIONALITY': EMP_NATIONALITY,
                              'EMP_GENDER': EMP_GENDER,
                              'EMP_PHYSICAL_DISABILITY_FLAG': EMP_PHYSICAL_DISABILITY_FLAG,
                              'EMP_MILITARY_SERVICE_START_DT': EMP_MILITARY_SERVICE_START_DT,
                              'EMP_MILITARY_SERVICE_END_DT': EMP_MILITARY_SERVICE_END_DT,
                              'EMP_MILITARY_SERVICE_TITLE': EMP_MILITARY_SERVICE_TITLE,
                              'EMP_MILITARY_SERVICE_COUNTRY': EMP_MILITARY_SERVICE_COUNTRY,
                              'EMP_PICTURE': EMP_PICTURE,
                              'EMP_MOBILE_NUMBER': EMP_MOBILE_NUMBER,
                              'EMP_EMAIL_ID': EMP_EMAIL_ID,
                              'EMP_OFFICE_LOCATION': EMP_OFFICE_LOCATION,
                              'EMP_OFFICE_PHONE_NUMBER': EMP_OFFICE_PHONE_NUMBER,
                              'EMP_TITLE': EMP_TITLE,
                              'EMP_FIRST_NAME': EMP_FIRST_NAME,
                              'EMP_MIDDLE_NAME': EMP_MIDDLE_NAME,
                              'EMP_ARABIC_FATHER_NAME': EMP_ARABIC_FATHER_NAME,
                              'EMP_ARABIC_MOTHER_NAME': EMP_ARABIC_MOTHER_NAME,
                              'EMP_PARENTAL_GRANDFATHERS_NAME': EMP_PARENTAL_GRANDFATHERS_NAME,
                              'EMP_FAMILY_NAME': EMP_FAMILY_NAME,
                              'EMP_FULL_NAME': EMP_FULL_NAME,
                              'EMP_PREFERRED_NAME': EMP_PREFERRED_NAME,
                              'EMP_FATHERS_NAME': EMP_FATHERS_NAME,
                              'EMP_MOTHERS_NAME': EMP_MOTHERS_NAME,
                              'EMP_ARABIC_FULL_NAME': EMP_ARABIC_FULL_NAME,
                              'EMP_ARABIC_LAST_NAME': EMP_ARABIC_LAST_NAME,
                              'EMP_UAE_ADD_BUILDING_OR_VILLA': EMP_UAE_ADD_BUILDING_OR_VILLA,
                              'EMP_UAE_ADD_STREET': EMP_UAE_ADD_STREET,
                              'EMP_UAE_ADD_CITY': EMP_UAE_ADD_CITY,
                              'EMP_UAE_ADD_EMIRATE': EMP_UAE_ADD_EMIRATE,
                              'EMP_UAE_ADD_RESIDENTIAL_TYPE': EMP_UAE_ADD_RESIDENTIAL_TYPE,
                              'START_DATE': START_DATE,
                              'END_DATE': END_DATE,
                              'EMP_UAE_ADD_RENTAL_VALUE': EMP_UAE_ADD_RENTAL_VALUE,
                              'EMP_UAE_ADD_TAWTHEEQ_NO': EMP_UAE_ADD_TAWTHEEQ_NO,
                              'EMP_VISA_NUMBER': EMP_VISA_NUMBER,
                              'EMP_VISA_ISSUE_DT': EMP_VISA_ISSUE_DT,
                              'EMP_VISA_EXPIRY_DT': EMP_VISA_EXPIRY_DT,
                              'EMP_VISA_PLACE_OF_ISSUE': EMP_VISA_PLACE_OF_ISSUE,
                              'EMP_VISA_COMPANY_SPONSORED_FLG': EMP_VISA_COMPANY_SPONSORED_FLG,
                              'EMP_VISA_SPONSOR_NAME': EMP_VISA_SPONSOR_NAME,
                              'EMP_VISA_SPONSOR_CONTACT': EMP_VISA_SPONSOR_CONTACT,
                              'EMP_VISA_TITLE_ENGLISH': EMP_VISA_TITLE_ENGLISH,
                              'EMP_VISA_TITLE_ARABIC': EMP_VISA_TITLE_ARABIC})
            V_MASTER_EMPLOYEE_data_list.append(data_dict)

        return V_MASTER_EMPLOYEE_data_list

    def get_hrjob_data_list(self):
        """
        Author:Bhavesh Jadav TechUltra Solutions
        Date:31/08/2020
        Func: this method use for the prepare list of dictionary for the xls file from the hr.jobs
        :return: V_MASTER_JOB: list of dictionary the xls file
        """
        hrjob_obj = self.env['hr.job']
        jobs = hrjob_obj.search([])
        V_MASTER_JOB = []
        for job in jobs:
            data_dict = {}
            JOB_CODE = job.name or ''
            JOB_NAME = job.job_title and job.job_title.name or ''
            JOB_NAME_ARABIC = ''
            JOB_GRADE = job.job_grade and job.job_grade.name or ''
            JOB_FAMILY = ''
            JOB_DESCRIPTION = job.description or ''
            JOB_EVAL_TYPE = ''
            JOB_EVAL_SCORE = ''
            JOB_TITLE = job.job_title and job.job_title.name or ''
            JOB_ISCO_CODE = job.isco_code and job.isco_code.code or ''
            JOB_ISCO_NAME = job.isco_code and job.isco_code.name or ''
            JOB_ENTRY_QUALIFICATION = ''
            JOB_OCH_INDUSTRY = ''
            JOB_OCH_OCCUPATION = ''
            JOB_QUALIFICATION_TITLE = ''
            JOB_END_DATE = ''
            if job and job.employee_ids:
                if job.employee_ids[0].active:
                    JOB_START_DATE = job.employee_ids and job.employee_ids[0].contract_id and job.employee_ids[
                        0].contract_id.date_start and job.employee_ids[0].contract_id.date_start.strftime(
                        "%d/%m/%Y") or ''
                else:
                    JOB_START_DATE = job.employee_ids and job.employee_ids[0].contract_id and job.employee_ids[
                        0].contract_id.effective_end_date and job.employee_ids[0].effective_end_date.strftime(
                        "%d/%m/%Y") or ''
            else:
                JOB_START_DATE = ''
            data_dict.update({'JOB_CODE': JOB_CODE,
                              'JOB_TITLE_NAME': JOB_NAME,
                              'JOB_TITLE_NAME_ARABIC': JOB_NAME_ARABIC,
                              'JOB_GRADE': JOB_GRADE,
                              'JOB_FAMILY': JOB_FAMILY,
                              'JOB_DESCRIPTION': JOB_DESCRIPTION,
                              'JOB_EVAL_TYPE': JOB_EVAL_TYPE,
                              'JOB_EVAL_SCORE': JOB_EVAL_SCORE,
                              'JOB_TITLE': JOB_TITLE,
                              'JOB_ISCO_CODE': JOB_ISCO_CODE,
                              'JOB_ISCO_NAME': JOB_ISCO_NAME,
                              'JOB_ENTRY_QUALIFICATION': JOB_ENTRY_QUALIFICATION,
                              'JOB_OCH_INDUSTRY': JOB_OCH_INDUSTRY,
                              'JOB_OCH_OCCUPATION': JOB_OCH_OCCUPATION,
                              'JOB_QUALIFICATION_TITLE': JOB_QUALIFICATION_TITLE,
                              'JOB_START_DATE': JOB_START_DATE,
                              'JOB_END_DATE': JOB_END_DATE})
            V_MASTER_JOB.append(data_dict)
        return V_MASTER_JOB

    def get_jobgrade_data_list(self):
        """
        Author:Bhavesh Jadav TechUltra Solutions
        Date:31/08/2020
        Func: this method use for the prepare list of dictionary for the xls file from the job.grade
        :return: V_MASTER_GRADE: list of dictionary the xls file
        """
        hr_grade_obj = self.env['job.grade']
        grades = hr_grade_obj.search([])
        V_MASTER_GRADE = []
        for grade in grades:
            data_dict = {}
            GRADE_CODE = grade.name or ''
            GRADE_NAME = grade.name or ''
            GRADE_LEVEL = grade.level or ''
            data_dict.update({'GRADE_CODE': GRADE_CODE,
                              'GRADE_NAME': GRADE_NAME,
                              'GRADE_LEVEL': GRADE_LEVEL})
            V_MASTER_GRADE.append(data_dict)
        return V_MASTER_GRADE

    def get_emp_contacts(self):
        """
            Author:Bhavesh Jadav TechUltra Solutions
            Date:31/08/2020
            Func: this method use for the prepare list of dictionary for the xls file from the hr.employee
            :return: V_EMP_CONTACTS: list of dictionary the xls file
                """
        V_EMP_CONTACTS = []
        hr_employee_obj = self.env['hr.employee']
        employee_ids = hr_employee_obj.search([])
        for employee_id in employee_ids:
            data_dict = {}
            EMPLOYEE_ID = employee_id.system_id or ''
            CONTACT_EMAIL_ID = employee_id.work_email or ''
            CONTACT_OFFICE_NUMBER = employee_id.work_phone or ''
            CONTACT_MOBILE_NUMBER = employee_id.mobile_phone or ''
            CONTACT_FIRST_NAME = employee_id.firstname or ''
            CONTACT_LAST_NAME = employee_id.lastname or ''
            CONTACT_RELATIONSHIP = ''
            CONTACT_EMPLOYED_BY_MDC = ''
            CONTACT_EMPLOYED_BY_GOV = ''
            data_dict.update({'EMPLOYEE_ID': EMPLOYEE_ID,
                              'CONTACT_EMAIL_ID': CONTACT_EMAIL_ID,
                              'CONTACT_OFFICE_NUMBER': CONTACT_OFFICE_NUMBER,
                              'CONTACT_MOBILE_NUMBER': CONTACT_MOBILE_NUMBER,
                              'CONTACT_FIRST_NAME': CONTACT_FIRST_NAME,
                              'CONTACT_LAST_NAME': CONTACT_LAST_NAME,
                              'CONTACT_RELATIONSHIP': CONTACT_RELATIONSHIP,
                              'CONTACT_EMPLOYED_BY_MDC': CONTACT_EMPLOYED_BY_MDC,
                              'CONTACT_EMPLOYED_BY_GOV': CONTACT_EMPLOYED_BY_GOV})
            V_EMP_CONTACTS.append(data_dict)
        return V_EMP_CONTACTS

    def get_hr_compensation(self):
        """
        Author:Bhavesh Jadav TechUltra Solutions
        Date:31/08/2020
        Func: this method use for the prepare list of dictionary for the xls file from the hr.compensation
        :return: V_EMP_COMPENSATION: list of dictionary the xls file
        """
        hr_compensation_obj = self.env['hr.compensation']
        compensations = hr_compensation_obj.search([])
        compensations = compensations.filtered(lambda x: x.related_contract)
        V_EMP_COMPENSATION = []
        for compensation in compensations:
            data_dict = {}
            EMPLOYEE_ID = compensation.related_contract and compensation.related_contract.employee_id and compensation.related_contract.employee_id.system_id or ''
            CONTRACT_TYPE = compensation.related_contract and compensation.related_contract.employment_status or ''
            ELEMENT_TYPE = 'Earning'
            ELEMENT_CODE = compensation.name and compensation.name.code or ''
            ELEMENT_NAME = compensation.component_description or ''
            START_DATE = compensation.from_date and compensation.from_date.strftime("%d/%m/%Y") or ''
            END_DATE = compensation.to_date and compensation.to_date.strftime("%d/%m/%Y") or ''
            MONTHLY_VALUE = compensation.amount or ''
            CURRENCY = compensation.currency and compensation.currency.name or ''
            ACCRUAL_DAYS = str(compensation.frequency) + ' ' + str(compensation.period)
            data_dict.update({'EMPLOYEE_ID': EMPLOYEE_ID,
                              'CONTRACT_TYPE': CONTRACT_TYPE,
                              'ELEMENT_TYPE': ELEMENT_TYPE,
                              'ELEMENT_CODE': ELEMENT_CODE,
                              'ELEMENT_NAME': ELEMENT_NAME,
                              'START_DATE': START_DATE,
                              'END_DATE': END_DATE,
                              'MONTHLY_VALUE': MONTHLY_VALUE,
                              'CURRENCY': CURRENCY,
                              'ACCRUAL_DAYS': ACCRUAL_DAYS})
            V_EMP_COMPENSATION.append(data_dict)
        return V_EMP_COMPENSATION

    def get_hr_department(self):
        """
        Author:Bhavesh Jadav TechUltra Solutions
        Date:31/08/2020
        Func: this method use for the prepare list of dictionary for the xls file from the hr.department
        :return: V_MASTER_ORG: list of dictionary the xls file
        """
        V_MASTER_ORG = []
        hr_department_obj = self.env['hr.department']
        departments = hr_department_obj.search([])
        for department in departments:
            data_dict = {}
            ORG_CODE = department.code or ''
            ORG_NAME = department.name or ''
            PARENT_ORG_CODE = department.parent_id and department.parent_id.code or ''
            PARENT_ORG_NAME = department.parent_id and department.parent_id.name or ''
            ORG_LEVEL = department.type or ''
            ORG_START_DATE = department.start_date and department.start_date.strftime("%d/%m/%Y") or ''
            ORG_END_DATE = department.end_date and department.end_date.strftime("%d/%m/%Y") or ''
            ORG_MANAGER_ID = department.manager_id and department.manager_id.system_id or ''
            ORG_MANAGER_NAME = department.manager_id and department.manager_id.name or ''
            ORG_ARABIC_NAME = ''
            data_dict.update({'ORG_CODE': ORG_CODE,
                              'ORG_NAME': ORG_NAME,
                              'PARENT_ORG_CODE': PARENT_ORG_CODE,
                              'PARENT_ORG_NAME': PARENT_ORG_NAME,
                              'ORG_LEVEL': ORG_LEVEL,
                              'ORG_START_DATE': ORG_START_DATE,
                              'ORG_END_DATE': ORG_END_DATE,
                              'ORG_MANAGER_ID': ORG_MANAGER_ID,
                              'ORG_MANAGER_NAME': ORG_MANAGER_NAME,
                              'ORG_ARABIC_NAME': ORG_ARABIC_NAME})
            V_MASTER_ORG.append(data_dict)
        return V_MASTER_ORG

    def get_emp_dependents(self):
        """
        Author:Bhavesh Jadav TechUltra Solutions
        Date:31/08/2020
        Func: this method use for the prepare list of dictionary for the xls file from the hr.employee
        :return: V_EMP_DEPENDENTS: list of dictionary the xls file
        """
        V_EMP_DEPENDENTS = []
        hr_employee_obj = self.env['hr.employee']
        employee_ids = hr_employee_obj.search([])
        for employee_id in employee_ids:
            employee_dependents = employee_id.dependents
            for employee_dependent in employee_dependents:
                data_dict = {}
                dependent_passport_id = False
                dependent_visa_id = False
                dependent_emirates_id = False
                document_type_visa = self.env['document.types'].search([('name', '=', 'Visa')], limit=1)
                document_type_passport = self.env['document.types'].search([('name', '=', 'Passport')], limit=1)
                document_type_emirates = self.env['document.types'].search([('name', '=', 'Emirates ID')], limit=1)
                if document_type_passport:
                    dependent_passport_id = self.env['documents.document'].search(
                        [('res_id', '=', employee_dependent.id), ('res_model', '=', 'hr.employee'),
                         ('document_type_id', '=', document_type_passport.id)], limit=1, order='desc')
                if document_type_visa:
                    dependent_visa_id = self.env['documents.document'].search(
                        [('res_id', '=', employee_dependent.id), ('res_model', '=', 'hr.employee'),
                         ('document_type_id', '=', document_type_visa.id)], limit=1, order='desc')
                if document_type_emirates:
                    dependent_emirates_id = self.env['documents.document'].search(
                        [('res_id', '=', employee_dependent.id), ('res_model', '=', 'hr.employee'),
                         ('document_type_id', '=', document_type_emirates.id)], limit=1, order='desc')
                EMPLOYEE_ID = employee_id.system_id or ''
                DEPENDENT_FIRST_NAME = employee_dependent.name or ''
                DEPENDENT_LAST_NAME = ''
                DEPENDENT_DATE_OF_BIRTH = employee_dependent.date and employee_dependent.date.strftime("%d/%m/%Y") or ''
                RELATIONSHIP = employee_dependent.contact_relation_type_id and employee_dependent.contact_relation_type_id.name or ''
                DEPENDENT_GENDER = employee_dependent.gender or ''
                DEPENDENT_NATIONALITY = employee_dependent.nationality and employee_dependent.nationality.name or ''
                DEPENDENT_PASSPORT_NO = dependent_passport_id and dependent_passport_id.passport_no or ''
                DEPENDET_PASSPORT_EXPIRY_DT = dependent_passport_id and dependent_passport_id.expiry_date and dependent_passport_id.expiry_date.strftime(
                    "%d/%m/%Y") or ''
                DEPENDENT_VISA_NUMBER = dependent_visa_id and dependent_visa_id.visa_file_no or ''
                DEPENDENT_VISA_EXPIRY_DATE = dependent_visa_id and dependent_visa_id.expiry_date and dependent_visa_id.expiry_date.strftime(
                    "%d/%m/%Y") or ''
                DEPENDENT_UNIFIED_NUMBER = dependent_visa_id and dependent_visa_id.visa_unified_no or ''
                DEPENDENT_EMIRATE_ID = dependent_emirates_id and dependent_emirates_id.emirates_id or ''
                DEPENDENT_ARABIC_FULL_NAME = ''
                DEPENDENT_ARABIC_LAST_NAME = ''
                DEPENDENT_EMPLOYER_MDC_COMPANY = ''
                DEPENDENT_EMPLOYER_GOV_DEPT = ''
                data_dict.update({'EMPLOYEE_ID': EMPLOYEE_ID,
                                  'DEPENDENT_FIRST_NAME': DEPENDENT_FIRST_NAME,
                                  'DEPENDENT_LAST_NAME': DEPENDENT_LAST_NAME,
                                  'DEPENDENT_DATE_OF_BIRTH': DEPENDENT_DATE_OF_BIRTH,
                                  'RELATIONSHIP': RELATIONSHIP,
                                  'DEPENDENT_GENDER': DEPENDENT_GENDER,
                                  'DEPENDENT_NATIONALITY': DEPENDENT_NATIONALITY,
                                  'DEPENDENT_PASSPORT_NO': DEPENDENT_PASSPORT_NO,
                                  'DEPENDET_PASSPORT_EXPIRY_DT': DEPENDET_PASSPORT_EXPIRY_DT,
                                  'DEPENDENT_VISA_NUMBER': DEPENDENT_VISA_NUMBER,
                                  'DEPENDENT_VISA_EXPIRY_DATE': DEPENDENT_VISA_EXPIRY_DATE,
                                  'DEPENDENT_UNIFIED_NUMBER': DEPENDENT_UNIFIED_NUMBER,
                                  'DEPENDENT_EMIRATE_ID': DEPENDENT_EMIRATE_ID,
                                  'DEPENDENT_ARABIC_FULL_NAME': DEPENDENT_ARABIC_FULL_NAME,
                                  'DEPENDENT_ARABIC_LAST_NAME': DEPENDENT_ARABIC_LAST_NAME,
                                  'DEPENDENT_EMPLOYER_MDC_COMPANY': DEPENDENT_EMPLOYER_MDC_COMPANY,
                                  'DEPENDENT_EMPLOYER_GOV_DEPT': DEPENDENT_EMPLOYER_GOV_DEPT})
                V_EMP_DEPENDENTS.append(data_dict)

        return V_EMP_DEPENDENTS

    def get_emp_education(self):
        """
        Author:Bhavesh Jadav TechUltra Solutions
        Date:31/08/2020
        Func: this method use for the prepare list of dictionary for the xls file from the hr.employee
        :return: V_EMP_EDUCATION: list of dictionary the xls file
        """
        V_EMP_EDUCATION = []
        hr_employee_obj = self.env['hr.employee']
        employee_ids = hr_employee_obj.search([])
        education_type = self.env['hr.resume.line.type'].search([('type', '=', 'edu')], limit=1)
        certification_type = self.env['hr.resume.line.type'].search([('type', '=', 'nor')], limit=1)
        for employee_id in employee_ids:
            data_dict = {}
            education_lines = employee_id.resume_line_ids.filtered(
                lambda line: line.line_type_id == education_type or line.line_type_id == certification_type)
            for education_line in education_lines:
                EMPLOYEE_ID = employee_id.system_id or ''
                EDUCATION_LEVEL_TYPE = education_line.education_level and education_line.education_level.name or ''
                CERTIFICATE_NAME = education_line.name
                START_DATE = education_line.date_start and education_line.date_start.strftime("%d/%m/%Y") or ''
                END_DATE = education_line.date_end and education_line.date_end.strftime("%d/%m/%Y") or ''
                AWARDED_COUNTRY = ''
                AWARDED_DATE = ''
                GPA_AWARDED = ''
                AWARDING_ESTABLISHMENT = ''
                AWARDING_BODY = ''
                STATUS = education_line.educational_status or ''
                data_dict.update({'EMPLOYEE_ID': EMPLOYEE_ID,
                                  'EDUCATION_LEVEL_TYPE': EDUCATION_LEVEL_TYPE,
                                  'CERTIFICATE_NAME': CERTIFICATE_NAME,
                                  'START_DATE': START_DATE,
                                  'END_DATE': END_DATE,
                                  'AWARDED_COUNTRY': AWARDED_COUNTRY,
                                  'AWARDED_DATE': AWARDED_DATE,
                                  'GPA_AWARDED': GPA_AWARDED,
                                  'AWARDING_ESTABLISHMENT': AWARDING_ESTABLISHMENT,
                                  'AWARDING_BODY': AWARDING_BODY,
                                  'STATUS': STATUS})
                V_EMP_EDUCATION.append(data_dict)
        if not V_EMP_EDUCATION:
            data_dict = {}
            data_dict.update({'EMPLOYEE_ID': '',
                              'EDUCATION_LEVEL_TYPE': '',
                              'CERTIFICATE_NAME': '',
                              'START_DATE': '',
                              'END_DATE': '',
                              'AWARDED_COUNTRY': '',
                              'AWARDED_DATE': '',
                              'GPA_AWARDED': '',
                              'AWARDING_ESTABLISHMENT': '',
                              'AWARDING_BODY': '',
                              'STATUS': ''})
            V_EMP_EDUCATION.append(data_dict)
        return V_EMP_EDUCATION

    def get_emp_previous_employments(self):
        """
        Author:Bhavesh Jadav TechUltra Solutions
        Date:31/08/2020
        Func: this method use for the prepare list of dictionary for the xls file from the hr.employee
        :return: V_EMP_PREVIOUS_EMPLOYMENTS: list of dictionary the xls file
        """
        V_EMP_PREVIOUS_EMPLOYMENTS = []
        hr_employee_obj = self.env['hr.employee']
        employee_ids = hr_employee_obj.search([])
        experience_type = self.env['hr.resume.line.type'].search([('type', '=', 'exp')], limit=1)
        for employee_id in employee_ids:
            data_dict = {}
            previous_employments = employee_id.resume_line_ids.filtered(
                lambda line: line.line_type_id == experience_type and line.date_end and line.date_end < date.today())
            for previous_employment in previous_employments:
                EMPLOYEE_ID = employee_id.system_id or ''
                COMPANY_NAME = previous_employment.company_name or ''
                JOB_TITLE = previous_employment.job_title or ''
                JOB_LEVEL = ''
                START_DATE = previous_employment.date_start and previous_employment.date_start.strftime(
                    "%d/%m/%Y") or ''
                END_DATE = previous_employment.date_end and previous_employment.date_end.strftime("%d/%m/%Y") or ''
                GRADE = ''
                PREVIOUS_MDC_COMPANY_FLAG = ''
                data_dict.update({'EMPLOYEE_ID': EMPLOYEE_ID,
                                  'COMPANY_NAME': COMPANY_NAME,
                                  'JOB_TITLE': JOB_TITLE,
                                  'JOB_LEVEL': JOB_LEVEL,
                                  'START_DATE': START_DATE,
                                  'END_DATE': END_DATE,
                                  'GRADE': GRADE,
                                  'PREVIOUS_MDC_COMPANY_FLAG': PREVIOUS_MDC_COMPANY_FLAG})
                V_EMP_PREVIOUS_EMPLOYMENTS.append(data_dict)
        return V_EMP_PREVIOUS_EMPLOYMENTS

    def get_planned_vacancies(self):
        """
        Author:Bhavesh Jadav TechUltra Solutions
        Date:31/08/2020
        Func: this method use for the prepare list of dictionary for the xls file from the hr.job
        :return: V_ALL_PLANNED_VACANCIES: list of dictionary the xls file
        """
        V_ALL_PLANNED_VACANCIES = []
        hrjob_obj = self.env['hr.job']
        job_vacancies = hrjob_obj.search([('state', '=', 'recruit')])
        for job_vacancie in job_vacancies:
            data_dict = {}
            ORG_CODE = job_vacancie.department_id and job_vacancie.department_id.code or ''
            ORG_NAME = job_vacancie.department_id and job_vacancie.department_id.name or ''
            CREATION_DT = job_vacancie.create_date and job_vacancie.create_date.strftime("%d/%m/%Y") or ''
            VACANCY_NAME = job_vacancie.job_title and job_vacancie.job_title.name or ''
            VACANCY_RATIONALE = ''
            CONTRACT_TYPE = ''
            GRADE_CODE = job_vacancie.job_grade and job_vacancie.job_grade.name or ''
            GRADE_NAME = job_vacancie.job_grade and job_vacancie.job_grade.name or ''
            ISCO_CODE = job_vacancie.isco_code and job_vacancie.isco_code.name or ''
            JOB_LEVEL = ''
            MINIMUM_QUALIFICATIONS = ''
            MINIMUM_YEARS_EXPERIENCE = ''
            VACANCY_GENDER = ''
            EMIRATIZIBLE = ''
            WHY_NO_EMIRATIZIBLE = ''
            data_dict.update({'ORG_CODE': ORG_CODE,
                              'ORG_NAME': ORG_NAME,
                              'CREATION_DT': CREATION_DT,
                              'VACANCY_NAME': VACANCY_NAME,
                              'VACANCY_RATIONALE': VACANCY_RATIONALE,
                              'CONTRACT_TYPE': CONTRACT_TYPE,
                              'GRADE_CODE': GRADE_CODE,
                              'GRADE_NAME': GRADE_NAME,
                              'ISCO_CODE': ISCO_CODE,
                              'JOB_LEVEL': JOB_LEVEL,
                              'MINIMUM_QUALIFICATIONS': MINIMUM_QUALIFICATIONS,
                              'MINIMUM_YEARS_EXPERIENCE': MINIMUM_YEARS_EXPERIENCE,
                              'VACANCY_GENDER': VACANCY_GENDER,
                              'EMIRATIZIBLE': EMIRATIZIBLE,
                              'WHY_NO_EMIRATIZIBLE': WHY_NO_EMIRATIZIBLE})
            V_ALL_PLANNED_VACANCIES.append(data_dict)

        return V_ALL_PLANNED_VACANCIES

    def get_all_recruitment_details(self):
        """
        Author:Bhavesh Jadav TechUltra Solutions
        Date:01/09/2020
        Func: this method use for the prepare list of dictionary for the xls file from the hr.job
        :return: V_ALL_RECRUITMENT_DETAILS: list of dictionary the xls file
        """
        V_ALL_RECRUITMENT_DETAILS = []
        hr_applicant_rec = self.env['hr.applicant'].search([])
        # job_details = hr_applicant_obj.search([('state', '=', 'recruit')])
        for hr_applicant in hr_applicant_rec:
            data_dict = {}
            REQUISITION_NUMBER = ''
            ADTC_REGISTRATION_NUMBER = ''
            VACANCY_CREATION_DT = hr_applicant.create_date and hr_applicant.create_date.strftime("%d/%m/%Y") or ''
            VACANCY_PLANNED_OFFER_DATE = ''
            VACANCY_BUDGETED_INDICATOR = ''
            VACANCY_REPLACEMENT_NAME = ''
            VACANCY_TITLE = hr_applicant.job_id and hr_applicant.job_id.job_title and hr_applicant.job_id.job_title.name or ''
            VACANCY_GRADE = hr_applicant.job_id and hr_applicant.job_id.job_grade and hr_applicant.job_id.job_grade.name or ''
            VACANCY_ISCO_CODE = hr_applicant.job_id and hr_applicant.job_id.isco_code and hr_applicant.job_id.isco_code.name or ''
            VACANCY_STATUS = ''
            MINIMUM_QUALIFICATION = ''
            MAXIMUM_QUALIFICATION = ''
            MIN_YEARS_OF_EXPERIENCE = ''
            OTHER_SKILL = ''
            LOCATION_CITY = ''
            BUSINESS_UNIT = ''
            RECRUITER = ''
            NUMBER_OF_OPENINGS = ''
            MIN_MONTHLY_SALARY_AED = ''
            EMIRATIZABLE_FLAG = ''
            NON_EMIRATIZABLE_REASON = ''
            IS_BUDGETED_FLAG = ''
            BUDGET_YEAR = ''
            REQUISITION_TYPE = ''
            REQUISITION_JUSTIFICATION = ''
            REQUISITION_CLOSING_DT = ''
            POST_OFFER_DT = ''
            OFFER_ACTUAL_DT = ''
            SUPPLIER_NAME = ''
            SECONDARY_SUPPLIER_NAME = ''
            RRF_CREATION_DATE = ''
            INTAKE_SESSION_COMPLETION_DATE = ''
            PLANNED_START_DATE = ''
            OPENING_DATE = ''
            DAYS_OPEN = ''
            HOLD_DAYS = ''
            NUMBER_OF_APPLICANTS = hr_applicant.application_count
            UAE = self.env['res.country'].search([('name', '=', 'United Arab Emirates')])
            if UAE:
                NUMBER_OF_UAE_APPLICANTS = len(
                    self.env['hr.applicant'].search([('job_id', '=', hr_applicant.id), ('nationality', '=', UAE.id)]))
            else:
                NUMBER_OF_UAE_APPLICANTS = ''
            NAME_OF_HIRE = ''
            FILLING_CANDIDATE_ASSET_NAME = ''
            TOTAL_COST_OF_HIRE_AED = ''
            DATE_OF_OFFER_ACCEPT = ''
            ACTUAL_START_DATE = ''
            data_dict.update({'REQUISITION_NUMBER': REQUISITION_NUMBER,
                              'ADTC_REGISTRATION_NUMBER': ADTC_REGISTRATION_NUMBER,
                              'VACANCY_CREATION_DT': VACANCY_CREATION_DT,
                              'VACANCY_PLANNED_OFFER_DATE': VACANCY_PLANNED_OFFER_DATE,
                              'VACANCY_BUDGETED_INDICATOR': VACANCY_BUDGETED_INDICATOR,
                              'VACANCY_REPLACEMENT_NAME': VACANCY_REPLACEMENT_NAME,
                              'VACANCY_TITLE': VACANCY_TITLE,
                              'VACANCY_GRADE': VACANCY_GRADE,
                              'VACANCY_ISCO_CODE': VACANCY_ISCO_CODE,
                              'VACANCY_STATUS': VACANCY_STATUS,
                              'MINIMUM_QUALIFICATION': MINIMUM_QUALIFICATION,
                              'MAXIMUM_QUALIFICATION': MAXIMUM_QUALIFICATION,
                              'MIN_YEARS_OF_EXPERIENCE': MIN_YEARS_OF_EXPERIENCE,
                              'OTHER_SKILL': OTHER_SKILL,
                              'LOCATION_CITY': LOCATION_CITY,
                              'BUSINESS_UNIT': BUSINESS_UNIT,
                              'RECRUITER': RECRUITER,
                              'NUMBER_OF_OPENINGS': NUMBER_OF_OPENINGS,
                              'MIN_MONTHLY_SALARY_AED': MIN_MONTHLY_SALARY_AED,
                              'EMIRATIZABLE_FLAG': EMIRATIZABLE_FLAG,
                              'NON_EMIRATIZABLE_REASON': NON_EMIRATIZABLE_REASON,
                              'IS_BUDGETED_FLAG': IS_BUDGETED_FLAG,
                              'BUDGET_YEAR': BUDGET_YEAR,
                              'REQUISITION_TYPE': REQUISITION_TYPE,
                              'REQUISITION_JUSTIFICATION': REQUISITION_JUSTIFICATION,
                              'REQUISITION_CLOSING_DT': REQUISITION_CLOSING_DT,
                              'POST_OFFER_DT': POST_OFFER_DT,
                              'OFFER_ACTUAL_DT': OFFER_ACTUAL_DT,
                              'SUPPLIER_NAME': SUPPLIER_NAME,
                              'SECONDARY_SUPPLIER_NAME': SECONDARY_SUPPLIER_NAME,
                              'RRF_CREATION_DATE': RRF_CREATION_DATE,
                              'INTAKE_SESSION_COMPLETION_DATE': INTAKE_SESSION_COMPLETION_DATE,
                              'PLANNED_START_DATE': PLANNED_START_DATE,
                              'OPENING_DATE': OPENING_DATE,
                              'DAYS_OPEN': DAYS_OPEN,
                              'HOLD_DAYS': HOLD_DAYS,
                              'NUMBER_OF_APPLICANTS': NUMBER_OF_APPLICANTS,
                              'NUMBER_OF_UAE_APPLICANTS': NUMBER_OF_UAE_APPLICANTS,
                              'NAME_OF_HIRE': NAME_OF_HIRE,
                              'FILLING_CANDIDATE_ASSET_NAME': FILLING_CANDIDATE_ASSET_NAME,
                              'TOTAL_COST_OF_HIRE_AED': TOTAL_COST_OF_HIRE_AED,
                              'DATE_OF_OFFER_ACCEPT': DATE_OF_OFFER_ACCEPT,
                              'ACTUAL_START_DATE': ACTUAL_START_DATE})
            V_ALL_RECRUITMENT_DETAILS.append(data_dict)

        return V_ALL_RECRUITMENT_DETAILS

    def get_emp_performance(self):
        """
        Author:Bhavesh Jadav TechUltra Solutions
        Date:01/09/2020
        Func: this method use for the prepare list of dictionary for the xls file from the appraisal.history
        :return: V_EMP_PERFORMANCE: list of dictionary the xls file
        """
        V_EMP_PERFORMANCE = []
        appraisal_history_obj = self.env['appraisal.history']
        appraisal_history_records = appraisal_history_obj.search([])
        for appraisal_history_record in appraisal_history_records:
            data_dict = {}
            EMPLOYEE_ID = appraisal_history_record.appraisal_employee and appraisal_history_record.appraisal_employee.system_id or ''
            PERFORMANCE_YEAR = appraisal_history_record.appraisal_year_related or ''
            PERFORMANCE = appraisal_history_record.hr_overall_rating_final_related or ''
            data_dict.update({'EMPLOYEE_ID': EMPLOYEE_ID,
                              'PERFORMANCE_YEAR': PERFORMANCE_YEAR,
                              'PERFORMANCE': PERFORMANCE})
            V_EMP_PERFORMANCE.append(data_dict)
        return V_EMP_PERFORMANCE

    def get_emp_termination(self):
        """
        Author:Nimesh Jadav TechUltra Solutions
        Date:16/09/2020
        Func: this method use for the prepare list of dictionary for the xls file from the regignation
        :return: V_EMP_TERMINATIONS: list of dictionary the xls file
        """
        V_EMP_TERMINATIONS = []
        hr_resignation_obj_records = self.env['hr.resignation'].search([])
        for termination in hr_resignation_obj_records:
            data_dict = {}
            EMPLOYEE_NAME = termination.related_employee.name or ''
            EMPLOYEE_ID = termination.related_employee.system_id or ''
            last_date_of_service = termination.end_date and termination.end_date.strftime("%d/%m/%Y") or ''
            reason = termination.related_approval and termination.related_approval.resignation_reason and termination.related_approval.resignation_reason.name or ''
            data_dict.update({'EMPLOYEE_ID': EMPLOYEE_ID,
                              'EMPLOYEE_NAME': EMPLOYEE_NAME,
                              'LAST_DATE_OF_SERVICE': last_date_of_service,
                              'TERMINATION_REASON': reason})
            V_EMP_TERMINATIONS.append(data_dict)
        return V_EMP_TERMINATIONS

    def get_master_location(self):
        """
        Author:Nimesh Jadav TechUltra Solutions
        Date:17/09/2020
        Func: this method use for the prepare list of dictionary for the xls file from the company location
        :return: V_COM_LOCATION: list of dictionary the xls file
        """
        V_MASTER_LOCATION = []
        com_location_records = self.env['company.location'].search([])
        for location in com_location_records:
            data_dict = {}
            location_name = location.location_name or ''
            emirate_name = location.emirate_name_id and location.emirate_name_id.name or ''
            city_name = location.location_city_id and location.location_city_id.name or ''
            country_name = location.location_country_id and location.location_country_id.name or ''
            address = location.location_address or ''
            phone = location.location_phone or ''
            code = location.location_code or ''
            data_dict.update({'LOCATION_NAME': location_name,
                              'EMIRATE_NAME': emirate_name,
                              'CITY_NAME': city_name,
                              'COUNTRY_NAME': country_name,
                              'LOCATION_ADDRESS': address,
                              'LOCATION_PHONE_NUMBER': phone,
                              'LOCATION_CODE': code})
            V_MASTER_LOCATION.append(data_dict)
        return V_MASTER_LOCATION

    def get_emp_assignments(self):
        """
        Author:Nimesh Jadav TechUltra Solutions
        Date:18/09/2020
        Func: this method use for the prepare list of dictionary for the xls file from the hr employee events
        :return: V_EMP_ASSIGNMENTS: list of dictionary the xls file
        """
        V_EMP_ASSIGNMENTS = []
        emp_event_records = self.env['hr.employee.event'].search([])
        for emp_event in emp_event_records:
            data_dict = {}
            employee_id = emp_event.employee_id.system_id or ''
            contract_type = emp_event.contract_type or ''
            hire_date = emp_event.employee_id and emp_event.employee_id.time_hired or ''
            start_date = emp_event.start_date and emp_event.start_date.strftime("%d/%m/%Y") or ''
            end_date = emp_event.end_date and emp_event.end_date.strftime("%d/%m/%Y") or ''
            job_name = emp_event.position_code_fkey and emp_event.position_code_fkey.name or ''
            job_title = emp_event.job_title_fkey and emp_event.job_title_fkey.name or ''
            grade = emp_event.employee_id and emp_event.employee_id.job_id and emp_event.employee_id.job_id.job_grade and emp_event.employee_id.job_id.job_grade.name or ''
            change_reason_code = emp_event.event_reason and emp_event.event_reason.name or ''
            change_reason_desc = emp_event.event_reason and emp_event.event_reason.description or ''
            superviser_name = emp_event.line_manager_id_fkey and emp_event.line_manager_id_fkey.name or ''
            section_name = emp_event.employee_id and emp_event.employee_id.contract_id and emp_event.employee_id.contract_id.section and emp_event.employee_id.contract_id.section.name or ''
            grade_desc = emp_event.employee_id and emp_event.employee_id.job_id and emp_event.employee_id.job_id.job_grade and emp_event.employee_id.job_id.job_grade.name or ''
            PERSON_TYPE = emp_event.employee_id and emp_event.employee_id.contract_id and emp_event.employee_id.contract_id.contract_subgroup and emp_event.employee_id.contract_id.contract_subgroup.name or ''
            data_dict.update({'EMPLOYEE_ID': employee_id,
                              'CONTRACT_TYPE': contract_type,
                              'PERSON_TYPE': PERSON_TYPE,
                              'LATEST_HIRE_DATE': start_date,
                              'START_DATE': start_date,
                              'END_DATE': end_date,
                              'CHANGE_REASON_CODE': change_reason_code,
                              'CHANGE_REASON_DESC': change_reason_desc,
                              'ORG_NAME ': section_name,
                              'JOB_NAME': job_name,
                              'JOB_TITLE': job_title,
                              'SUPERVISOR_NAME': superviser_name,
                              'GRADE_DESC': grade_desc
                              })
            V_EMP_ASSIGNMENTS.append(data_dict)
        return V_EMP_ASSIGNMENTS
