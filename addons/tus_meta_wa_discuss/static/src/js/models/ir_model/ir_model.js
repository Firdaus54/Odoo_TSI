/** @odoo-module **/

import { registerNewModel } from '@mail/model/model_core';
import { attr, one2one } from '@mail/model/model_field';
import { insert, unlink } from '@mail/model/model_field_command';

function factory(dependencies) {

    class IrModel extends dependencies['mail.model'] {

        static convertData(data) {
            const data2 = {};
            if ('id' in data) {
                data2.id = data.id;
            }
             if ('name' in data) {
                data2.name = data.name;
            }
            if ('model' in data) {
                data2.model = data.model;
            }
            return data2
        }

        static _createRecordLocalId(data) {
            return `${this.modelName}_${data.id}`;
        }

    }

    IrModel.fields = {
         id: attr({
            readonly: true,
            required: true,
        }),
        name: attr({

        }),
        model: attr({

        }),
    };
    IrModel.identifyingFields = ['id'];
    IrModel.modelName = 'ir.model';

    return IrModel;
}

registerNewModel('ir.model', factory);
