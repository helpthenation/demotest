odoo.define('roles_segregation.employee', function (require) {
    "use strict";

    var session = require('web.session');
    var BasicView = require('web.BasicView');
    BasicView.include({
        init: function (viewInfo, params) {
            var self = this;
            this._super.apply(this, arguments);
                session.user_has_group('roles_segregation.group_hc_compensation_and_benefits').then(function (has_group) {
                    if (has_group) {
                        self.controllerParams.archiveEnabled = 'False' in viewInfo.fields;
                    } else {
                        self.controllerParams.archiveEnabled = 'active' in viewInfo.fields;
                    }
                });
        },
    });


});