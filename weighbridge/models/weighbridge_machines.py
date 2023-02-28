from odoo import api, fields, models, _
import mysql.connector
from mysql.connector import Error
from odoo.exceptions import MissingError, UserError, ValidationError, AccessError
import datetime
import pytz
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DSD, \
    DEFAULT_SERVER_DATETIME_FORMAT as DTM


class WeighbridgeMachines(models.Model):
    _name = 'weighbridge.machines'

    host = fields.Char("Host")
    user = fields.Char("User")
    password = fields.Char("Password")
    database = fields.Char("DataBase")
    table = fields.Char("Table")

    def get_record(self):
        host = self.host
        user = self.user
        password = self.password
        database = self.database
        table = self.table
        port = "3306"
        server = "weighbridges-instance-1.csz2iven04gm.eu-central-1.rds.amazonaws.com:3306/weights"
        weighbridge = self.env['weighbridge.weighbridge']
        max_bridge = weighbridge.search([])
        max_id = 0
        if max_bridge:
            for mb in max_bridge:
                if mb.db_ticket_id > max_id:
                    max_id = mb.db_ticket_id
        query = 'SELECT * FROM %s.%s WHERE id_p > %s;' % [database, table, max_id]
        try:
            connection = mysql.connector.connect(host=host,
                                                 user=user,
                                                 password=password)
            if connection.is_connected():
                db_Info = connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                cursor = connection.cursor()
                cursor.execute(query)
                records = cursor.fetchall()
                print("You're connected to database: ", records)
        except Error as e:
            print("Error while connecting to MySQL", e)
        return records

    def action_create_weighbridge(self):
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        records = self.get_record()
        for rec in records:
            weight_time_convert_time_zone = datetime.datetime.strftime(
                pytz.utc.localize(
                    datetime.datetime.strptime(str(rec[8]), DTM)).astimezone(
                    local), "%Y-%m-%d %H:%M:%S")
            weight_time = datetime.datetime.strptime(str(weight_time_convert_time_zone), "%Y-%m-%d %H:%M:%S")

            weight_time_convert_time_zone2 = datetime.datetime.strftime(
                pytz.utc.localize(
                    datetime.datetime.strptime(str(rec[10]), DTM)).astimezone(
                    local), "%Y-%m-%d %H:%M:%S")
            weight_time2 = datetime.datetime.strptime(str(weight_time_convert_time_zone2), "%Y-%m-%d %H:%M:%S")
            self.env['weighbridge.weighbridge'].sudo().create({
                'db_ticket_id': rec[0],
                'car_plate_num': rec[3],
                'first_driver_name': rec[4],
                'first_weight': rec[5],
                'second_weight': rec[6],
                'first_datetime': weight_time,
                'second_datetime': weight_time2,
            })
