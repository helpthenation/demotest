# See LICENSE file for full copyright and licensing details.

from odoo import api, models


class hr_employee(models.Model):
    _inherit = 'hr.department'

    @api.model
    def get_dept_parent_childs(self, ids, parent_id):
        dept_details = []
        child_ids = []
        for department in self.browse(ids):
            job_title = False
            dept_parent_id = department.parent_id.id
            if parent_id[0] == department.id:
                dept_parent_id = False
            for child in department.child_ids:
                child_ids.append(child.id)
            if department.manager_id.job_id:
                job_title = department.manager_id.job_id.name

            if department.parent_id.manager_id:
                tree_parent = department.parent_id.manager_id.id
            else:
                tree_parent = "dept_" + str(department.parent_id.id)
            dept_details.append({
                'dept_id': "dept_" + str(department.id),
                'dept_name': department.name,
                'dept_parent_id': "dept_" + str(dept_parent_id),
                'dept_employee_id': department.manager_id.id,
                'dept_employee_name': department.manager_id.name,
                'dept_employee_email': department.manager_id.work_email,
                'dept_employee_job_title': job_title,
                'tree_parent': tree_parent,
                'dept_employee_type':
                    dict(self._fields['type'].selection).get(department.type),
            })
        return [dept_details, child_ids]

    @api.model
    def get_department_details(self, ids, parent_id):
        dept_details = []
        dept_parent_childs_object = self.get_dept_parent_childs
        loop = True
        while (loop):
            dept_parent_childs_details = dept_parent_childs_object(ids,
                                                                   parent_id)
            for data in dept_parent_childs_details[0]:
                dept_details.append(data)
            if dept_parent_childs_details[1]:
                ids = dept_parent_childs_details[1]
            else:
                loop = False
        return dept_details

    def employee_dept(self, ids):
        employee_obj = self.env['hr.employee']
        employee_ids = employee_obj.search([])
        department_ids = self.search([])
        dept_details = []
        emp_details = []

        for employee in employee_ids:
            if employee.parent_id:
                if employee.parent_id.department_id == employee.department_id:
                    tree_parent = employee.parent_id.id
                else:
                    tree_parent = "dept_" + str(employee.department_id.id)
                emp_color = employee.get_color()
                emp_details.append({
                    'emp_name': employee.name,
                    'emp_id': employee.id,
                    'parent': employee.parent_id.id,
                    'emp_email': employee.work_email,
                    'emp_job_title': employee.contract_id.job_title.name,
                    'emp_dept_name': employee.department_id.name,
                    'emp_dept_code': employee.department_id.code,
                    # 'emp_job_grade': employee.contract_id.job_grade.name,
                    'emp_job_position': employee.contract_id.job_id.name,
                    'emp_company_id': employee.company_employee_id,
                    'tree_parent': tree_parent,
                    'emp_color': emp_color
                })
            else:
                tree_parent = tree_parent = "dept_" + str(employee.department_id.id)
                emp_color = employee.get_color()
                emp_details.append({
                    'emp_name': employee.name,
                    'emp_id': employee.id,
                    'parent': employee.parent_id.id,
                    'emp_email': employee.work_email,
                    'emp_dept_name': employee.department_id.name,
                    'emp_dept_code': employee.department_id.code,
                    'emp_job_title': employee.contract_id.job_title.name,
                    'emp_job_grade': employee.contract_id.job_grade.name,
                    'emp_job_position': employee.contract_id.job_id.name,
                    'emp_company_id': employee.company_employee_id,
                    'tree_parent': tree_parent,
                    'emp_color': emp_color
                })

        if ids:
            parent_id = ids
            dept_details = self.get_department_details(ids, parent_id)
            return [emp_details, dept_details]
        else:
            for department in department_ids:
                its_manager_dept = False
                if department.parent_id.manager_id:
                    tree_parent = "mang_" + str(department.parent_id.manager_id.id)
                    its_manager_dept = True
                else:
                    tree_parent = "dept_" + str(department.parent_id.id)
                emp_color = department.manager_id.get_color()
                dept_details.append({
                    'dept_id': "dept_" + str(department.id),
                    'dept_name': department.name,
                    'dept_code': department.code,
                    'dept_parent_id': "dept_" + str(department.parent_id.id),
                    'dept_employee_id': str(department.manager_id.id),
                    'dept_employee_name': department.manager_id.name,
                    'dept_employee_job_position': department.manager_id.job_id.name,
                    'dept_company_employee_id': department.manager_id.company_employee_id,
                    # 'dept_employee_email': department.manager_id.work_email,
                    'dept_employee_job_title':
                        department.manager_id.contract_id.job_title.name,
                    'tree_parent': tree_parent,
                    'dept_emp_color': emp_color,
                    'its_manager_dept': its_manager_dept,
                    'dept_employee_type':
                        dict(self._fields['type'].selection).get(department.type),
                })
            return [emp_details, dept_details]


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def get_color(self):
        """
        Author: Bhavesh Jadav TechUltra Solution
        Date: 25/08/2020
        :return: color : use for the  Color name
        """
        self = self.sudo()
        group = self.contract_id.contract_group.id
        subgroup = self.contract_id.contract_subgroup.id
        employment_type = self.contract_employment_type.id
        resignations = self.contract_id.related_resign_request.filtered(
            lambda x: x.state in ('open', 'active', 'extended'))
        if len(resignations) > 0:
            color_combo = self.env['employee.color.combo'].search(
                [('leaver', '=', True)], limit=1)
        else:
            color_combo = self.env['employee.color.combo'].search(
                [('subgroup_id', '=', subgroup), ('group_id', '=', group),
                 ('employment_type_id', '=', employment_type)], limit=1)

        if color_combo:
            color = color_combo.name.color
        else:
            color_combo = self.env['employee.color.combo'].search([('default_color_combo', '=', True)], limit=1)
            color = color_combo.name.color if color_combo else 'gray'
        return color
