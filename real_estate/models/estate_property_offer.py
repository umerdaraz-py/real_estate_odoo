from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

from odoo.tools import float_is_zero


class EstatePropertiesOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Model for Real-Estate Properties offers"

    price = fields.Float(string="Price")
    status = fields.Selection([
        ('accepted', 'Accepted'),
        ('refused', 'Refused')
    ], string="Status", copy=False)
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one('estate.property', required=True, ondelete="cascade")
    property_type_id = fields.Many2one(related='property_id.property_type_id', store=True)
    validity = fields.Integer(string="Validity(days)", default=7)
    date_deadline = fields.Date(string="Deadline", compute='_compute_date_deadline', inverse='_inverse_date_deadline')

    _sql_constraints = [
        ('positive_price', 'CHECK(price > 0)', 'The price must be positive!'),
    ]

    @api.constrains('price')
    def _check_price(self):
        for record in self:
            if record.price <= 0:
                raise ValidationError("The price must be positive!")

    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for deadline in self:
            if deadline.create_date:
                deadline.date_deadline = (deadline.create_date + relativedelta(days=deadline.validity)).date()

    @api.model
    def create(self, vals):
        property = self.env['estate.property'].browse(vals['property_id'])
        if vals['price'] < property.best_price:
            raise UserError("Cannot create offer with a lower amount than an existing offer")
        property.state = 'offer received'
        return super().create(vals)

    # @api.model
    # def create(self, vals):
    #     property = self.env['estate.property.offer'].browse(vals['property_id'])
    #     if 'price' in vals and vals['price'] < property.best_price:
    #         raise UserError("Cannot create offer with a lower amount than an existing offer")
    #     property.state = 'offer accepted'
    #     return super(EstatePropertiesOffer, self).create(vals)

    def _inverse_date_deadline(self):
        for rec in self:
            if rec.create_date and rec.date_deadline:
                rec.validity = (rec.date_deadline - rec.create_date.date()).days

    def make_accept(self):
        for accept in self:
            offers = accept.property_id.offer_ids - accept
            for offer in offers:
                offer.make_refuse()
            accept.status = 'accepted'
            accept.property_id.state = 'offer accepted'
            accept.property_id.selling_price = accept.price
            accept.property_id.buyer_id = accept.partner_id
        return True

    def make_refuse(self):
        for rec in self:
            rec.status = 'refused'

        if 'accepted' not in rec.property_id.offer_ids.mapped('status'):
            rec.property_id.selling_price = None
            rec.property_id.buyer_id = None
            rec.property_id.state = 'offer received'
        return True
