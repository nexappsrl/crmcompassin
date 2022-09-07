# -*- coding: utf-8 -*-
import logging
import decimal
import datetime
import json

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class CustomEncoder(json.JSONEncoder):
    """Encoder json dedicato"""

    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        elif isinstance(obj, (decimal.Decimal, float)):
            return float(obj)
        elif isinstance(obj, (str,)):
            return obj.__str__().strip()
        return obj


class CustomDecoder(json.JSONDecoder):
    """Decoder json dedicato"""

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(
            self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        return dct

class extend_product(models.Model):    
    _description = 'Estende l\'entità prodotto.'
    _inherit ="product.template"

    na_linkdanea_category= fields.Text(string="Categoria")
    na_linkdanea_subcategory=fields.Text(string="Sottocategoria")
    na_linkdanea_width=fields.Text(string="Larghezza")
    na_linkdanea_height=fields.Text(string="Altezza")


    @classmethod
    def na_linkdanea_read_articoli_detail_category(self,raw:dict)->dict:
        ref="na_linkdanea"
        """Mappa la definizione degli articoli, in un dizionario consono. Le chiavi del dizionario, devono coincidere con i parametri del modello che estende il prodotto."""        
        buffer:dict={
            "{}_category".format(ref):raw["nomecategoria"].__str__().strip(),
            "{}_subcategory".format(ref):raw["nomesottocategoria"].__str__().strip(),
            "{}_width".format(ref):raw["extra1"].__str__().strip().lower().replace("base","").replace("larghezza","").strip(),
            "{}_height".format(ref):raw["extra2"].__str__().strip().lower().replace("altezza","").strip(),
        }
        return buffer
        