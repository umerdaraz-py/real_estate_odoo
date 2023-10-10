from dateutil.relativedelta import relativedelta

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real-Estate Properties"
    _order = "id desc"

    name = fields.Char(string="Title", required=True)
    tag_ids = fields.Many2many('estate.property.tag')
    description = fields.Text(string="Description")
    date_availability = fields.Date(string="Available From",
                                    default=fields.Date.today() + relativedelta(months=3), copy=False)
    expected_price = fields.Float(string="Expected Price", required=True)
    postcode = fields.Char(string="Postcode")
    selling_price = fields.Float(string="Selling Price", readonly=True, copy=False)
    bedrooms = fields.Integer(string="Bedrooms", default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West')
    ], string="Garden Orientation")
    active = fields.Boolean(default=True)
    state = fields.Selection([
        ('new', 'New'),
        ('offer received', 'Offer Received'),
        ('offer accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('canceled', 'Canceled')
    ], string="Status", required=True, copy=False, default='new')
    property_type_id = fields.Many2one("res.partner", string="Property Type")
    buyer_id = fields.Many2one('res.partner', string="Buyer", copy=False)
    salesman_id = fields.Many2one('res.users', string="Salesman", default=lambda self: self.env.user)
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offer ID")
    total_area = fields.Integer("Total Area (sqm)", compute="_total_area")
    best_price = fields.Float("Best Offer", compute="_compute_best_price", store=True)

    sql_constraints = [
        ('positive_expected_price', 'CHECK(expected_price > 0)', 'Expected price must be strictly positive!'),
        ('positive_selling_price', 'CHECK(selling_price >= 0)', 'Selling price must be positive'),
        ]

    # @api.constrains('expected_price', 'selling_price')
    # def _check_price(self):
    #     for record in self:
    #         if record.expected_price <= 0:
    #             raise ValidationError("The Expected Price must be positive!")
    #         if record.selling_price <= 0:
    #             raise ValidationError("The Selling Price must be positive!")

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for rec in self:
            if rec.selling_price and rec.selling_price < 0.9 * rec.expected_price:
                raise ValidationError('The selling price cannot be lower than 90% of the expected price')

            if rec.expected_price <= 0:
                raise ValidationError("The Expected Price must be positive!")
            if rec.selling_price <= 0:
                raise ValidationError("The Selling Price must be positive!")

    @api.depends("living_area", "garden_area")
    def _total_area(self):
        for rec in self:
            rec.total_area = rec.living_area + rec.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for rec in self:
            rec.best_price = max(rec.offer_ids.mapped("price"), default=None)

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = None
            self.garden_orientation = None

    def make_property_sold(self):
        if self.state == 'canceled':
            raise UserError('Cancel properties cannot be sold')
        else:
            self.state = 'sold'
        return True

    def make_property_cancel(self):
        if self.state == 'sold':
            raise UserError('Sold properties cannot be canceled')
        else:
            self.state = 'canceled'
        return True
