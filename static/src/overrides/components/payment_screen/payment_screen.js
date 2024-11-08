/** @odoo-module */

import {patch} from "@web/core/utils/patch";
import {PaymentScreen} from "@point_of_sale/app/screens/payment_screen/payment_screen";
import {Order} from "@point_of_sale/app/store/models";

const {useState} = owl;

patch(PaymentScreen.prototype, {
    setup() {
        super.setup();
        this.validationState = useState({block: false});
        const custom_uuid = self ? self.crypto.randomUUID() : false
        this.custom_uuid = useState({uuid: custom_uuid})
    },
    get validationBlockState() {
        return this.validationState.block
    },
    async sendRequestToDevice(order) {
        let paymentLine = order.selected_paymentline

        if (!paymentLine) {
            alert("No haz marcado ningun metodo de pago")
            return
        }

        let paymentMethod = paymentLine?.payment_method
        console.log("paymentMethod",paymentLine);
        // debugger
        let equipmentRecord = {};
        if (paymentMethod?.id) {
            let payment_equipment = await this.orm.call("pos.payment.method", "get_equipment_info", [
                [paymentMethod.id]]);
            equipmentRecord = payment_equipment
        }
        console.log("equipmentRecord", equipmentRecord);
        if (equipmentRecord.id) {
            this.validationState.block = true
            let timeoutId = setTimeout(() => {
                this.validationState.block = false
            }, equipmentRecord.validation_delay * 1000)

            const {model, token, serial} = equipmentRecord
            const url = `https://api.pushy.me/push?api_key=${token}`;
            const custom_uuid = this.custom_uuid.uuid ? this.custom_uuid.uuid : false

            const data = {
                to: serial,
                data: {
                    notiTitle: "Nuevo Pago",
                    notiMessage: `Tienes un pago pendiente por $${paymentLine.amount}`,
                    command: "sale",
                    paymentApp: model,
                    // paymentName: paymentLine.name,
                    // partner: order.partner?.id,
                    data: {
                        amount: paymentLine.amount,
                        ticket: order.name,
                        printVoucher: false,
                        employeeId: order.user_id,
                        saleType: 0,
                        uuid: custom_uuid
                    },
                },
                notification: {
                    title: "Pago pendiente",
                    body: `Tienes un pago pendiente por $${paymentLine.amount}`,
                    message: `Tienes un pago por $${paymentLine.amount}`,
                    badge: 1,
                    sound: "ping.aiff"
                }
            };
            const headers = {
                "Content-Type": "application/json",
            };
            debugger
            try {
                const response = await fetch(url, {
                    method: "POST",
                    headers: headers,
                    body: JSON.stringify(data),
                });

                if (!response.ok) {
                    alert(`Error con la validacion del pago. Error: ${(await response.json()).error}`)
                    throw new Error(`HTTP error! status: ${(await response.json()).error}`);
                }
                // clearTimeout(timeoutId)
                // this.validationState.block = false
                const responseData = await response.json();
                debugger
                console.log("Response Data OK:", responseData);

                await this.validateOrder()
            } catch (error) {
                console.error("Error in sending POST request:", error);
            }
        } else {
            alert('El metodo de pago no tiene configurado equipo POS')
        }

    },
    // async validateOrder(isForceValidate){
    // 	await super.validateOrder(...arguments);


    // },
    async _finalizeValidation() {
        //FROM ORIGEN FUNC
        if (this.currentOrder.is_paid_with_cash() || this.currentOrder.get_change()) {
            this.hardwareProxy.openCashbox();
        }

        this.currentOrder.date_order = luxon.DateTime.now();
        for (const line of this.paymentLines) {
            if (!line.amount === 0) {
                this.currentOrder.remove_paymentline(line);
            }
        }
        this.currentOrder.finalized = true;

        this.env.services.ui.block();
        let syncOrderResult;
        try {
            // 1. Save order to server.
            syncOrderResult = await this.pos.push_single_order(this.currentOrder);
            if (this.custom_uuid.uuid) {
                await this.orm.write("pos.order", [syncOrderResult[0].id], {custom_order_uuid: this.custom_uuid.uuid});
            }

            if (!syncOrderResult) {
                return;
            }
            // 2. Invoice.
            if (this.shouldDownloadInvoice() && this.currentOrder.is_to_invoice()) {
                if (syncOrderResult[0]?.account_move) {
                    await this.report.doAction("account.account_invoices", [
                        syncOrderResult[0].account_move,
                    ]);
                } else {
                    throw {
                        code: 401,
                        message: "Backend Invoice",
                        data: {order: this.currentOrder},
                    };
                }
            }
        } catch (error) {
            if (error instanceof ConnectionLostError) {
                this.pos.showScreen(this.nextScreen);
                Promise.reject(error);
                return error;
            } else {
                throw error;
            }
        } finally {
            this.env.services.ui.unblock();
        }

        // 3. Post process.
        if (
            syncOrderResult &&
            syncOrderResult.length > 0 &&
            this.currentOrder.wait_for_push_order()
        ) {
            await this.postPushOrderResolve(syncOrderResult.map((res) => res.id));
        }


        //Set data from Response Request
        if (this.currentOrder.is_to_invoice()) {
            let paymentMethod = this.currentOrder.selected_paymentline?.payment_method
            if (paymentMethod.id) {
                // let responseData = await this.orm.call("pos.payment.method", "execute_request_receipt_create", [
                //     [paymentMethod.id], [this.currentOrder.name]]);
                let responseData = await this.orm.call("pos.payment.method", "execute_request_receipt_create", [this.currentOrder.name]);
                debugger
                if (responseData.status == 'success') {
                    this.pos.selectedOrder.folio_number = responseData.num_folio
                    this.pos.selectedOrder.qr_receipt = atob(responseData.qr)
                } else {
                    alert(`La peticion para crear la boleta fallo!. Error: ${responseData.message}`)
                }
                console.log("Response Request", responseData)
            }
        }
        //FROM ORIGEN FUNC
        await this.afterOrderValidation(!!syncOrderResult && syncOrderResult.length > 0);
    }

})

patch(Order.prototype, {
    setup() {
        super.setup(...arguments);
        this.folio_number = null;
        this.qr_receipt = null;
    },
    export_for_printing() {
        let res = super.export_for_printing(...arguments)
        if (this.qr_receipt) {
            const codeWriter = new window.ZXing.BrowserQRCodeSvgWriter();
            let qr_code_svg = new XMLSerializer().serializeToString(codeWriter.write(this.qr_receipt, 150, 150));
            const _qr = 'data:image/svg+xml;base64,' + window.btoa(qr_code_svg);
            Object.assign(res, {
                folio: this.folio_number,
                qr_receipt: _qr
            })
        }

        return res
    }
})	