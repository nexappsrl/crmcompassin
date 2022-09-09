# -*- coding: utf-8 -*-
from email.policy import default
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

class stats_base(models.Model):
    _description ='Contenitore dei dati di riferimento, ritenuti idonei'
    _name="na_linkdanea.stats_base"

    ref_middle=fields.Text(string="Dati di connessione")
    ref_available = fields.Boolean(string='Record disponibile per l\'elaborazione',readonly=True,default=True)
    ref_status = fields.Text(string='Stato record',readonly=True,default="RDY")
    seriale_fattura=fields.Text(string="seriale fattura",readonly=True,default="EMPTY")
    tipo_doc = fields.Text(string='tipo_doc')
    numero_doc = fields.Text(string='numero_doc')
    data_fattura = fields.Date(string='data_fattura')
    cliente_fatturazione = fields.Text(string='cliente_fatturazione')
    indirizzo_ragione_sociale = fields.Text(string='Indirizzo Ragione Sociale')
    indirizzo_street = fields.Char(string="Indirizzo")
    indirizzo_street2 = fields.Char(string="Indirizzo alternativo")
    indirizzo_zip = fields.Char(string="Cap",change_default=True)
    indirizzo_city = fields.Char(string="Città")
    indirizzo_state_id = fields.Many2one("res.country.state", string='Stato', ondelete='restrict', domain="[('country_id', '=?', indirizzo_country_id)]")
    indirizzo_country_id = fields.Many2one('res.country', string='Nazione', ondelete='restrict')
    indirizzo_country_code = fields.Char(related='indirizzo_country_id.code', string="Codice Nazione")
    codice_prodotto = fields.Text(string='Codice prodotto')
    categoria = fields.Text(string='Categoria')
    sottocategoria = fields.Text(string='Sottocategoria')
    larghezza = fields.Text(string='Larghezza')
    altezza = fields.Text(string='Altezza')
    imponibile = fields.Monetary(string='Imponibile',currency_field='valuta')
    codice_imposta = fields.Text(string='Codice Imposta')
    valuta = fields.Many2one('res.currency', string='Valuta',compute="_compute_currency_set_euro")
    totale_fatturato=fields.Monetary(string='Fatturato totale',currency_field='valuta')

    @api.depends('totale_fatturato')
    @api.depends('imponibile')
    def _compute_currency_set_euro(self,*args,**kwargs):
        currency=None
        if self._context.get('default_currency_id'):
            currency=self._context.get('default_currency_id')
        else:
            currency=self.env.ref('base.EUR').id
        for record in self:
            record.save_valuta(currency)

    
    def create(self, vals_list):
        res_ids=super(stats_base,self).create(vals_list)
        res_ids.save_valuta(currency=self._get_valuta())
        return res_ids
    
    def write(self,vals):
        res=super(stats_base,self).write(vals)        
        res.save_valuta(currency=self._get_valuta())
        return res

    def _get_valuta(self):        
        if self._context.get('default_currency_id'):
            currency=self._context.get('default_currency_id')
        else:
            currency=self.env.ref('base.EUR').id
        return currency
    
    def save_valuta(self,currency:int=None,*args,**kwargs):
        if currency is None:
            if self._context.get('default_currency_id'):
                currency=self._context.get('default_currency_id')
            else:
                currency=self.env.ref('base.EUR').id
        if self.valuta is None:
            self.valuta=currency

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
        
class extend_lead(models.Model):
    _description = 'Estende l\'entità Lead.'
    _inherit ="crm.lead"

    na_linkdanea_iddoc = fields.Text(string="IDDoc")
    na_linkdanea_idrighe = fields.Text(string="IDDocRighe")
    na_linkdanea_numdoc= fields.Text(string="NumDoc")
    na_linkdanea_descdoc= fields.Text(string="DescDoc")

    @classmethod
    def na_linkdanea_read_lead_detail(self,raw:dict)->dict:
        """Mappa la definizione degli articoli, in un dizionario consono. Le chiavi del dizionario, devono coincidere con i parametri del modello che estende il prodotto."""        
        ref="na_linkdanea"
        buffer:dict={
            "{}_iddoc".format(ref):raw["keys"]["testata"].__str__().strip(),
            "{}_idrighe".format(ref):",".join(raw["keys"]["righe"]),
            "{}_numdoc".format(ref):raw["values"]["testata"]["NumDoc"],
            "{}_descdoc".format(ref):raw["values"]["testata"]["DescDoc"]}
        buffer["expected_revenue"]=raw["values"]["testata"]["TotNetto"]
        if raw["values"]["testata"]["TipoDoc"]=="Q":
            buffer["stage_id"]=3
        elif raw["values"]["testata"]["TipoDoc"]=="C":
            buffer["stage_id"]=4
        return buffer