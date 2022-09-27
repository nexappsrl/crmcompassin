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
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        return dct


class stats_base(models.Model):
    _description = "Contenitore dei dati di riferimento, ritenuti idonei"
    _name = "na_linkdanea.stats_base"

    ref_middle = fields.Text(string="Dati di connessione")
    ref_available = fields.Boolean(
        string="Record disponibile per l'elaborazione", readonly=True, default=True
    )
    ref_status = fields.Text(string="Stato record", readonly=True, default="RDY")
    seriale_fattura = fields.Text(
        string="seriale fattura", readonly=True, default="EMPTY",index=True
    )
    tipo_doc = fields.Text(string="tipo_doc",index=True)
    numero_doc = fields.Text(string="numero_doc",index=True)
    data_fattura = fields.Date(string="data_fattura")
    cliente_fatturazione = fields.Text(string="cliente_fatturazione")
    vat = fields.Text(string="Indirizzo Ragione Sociale")
    indirizzo_street = fields.Char(string="Indirizzo")
    indirizzo_street2 = fields.Char(string="Indirizzo alternativo")
    indirizzo_zip = fields.Char(string="Cap", change_default=True)
    indirizzo_city = fields.Char(string="Città")
    indirizzo_state_id = fields.Many2one(
        "res.country.state",
        string="Stato",
        ondelete="restrict",
        domain="[('country_id', '=?', indirizzo_country_id)]",
    )
    indirizzo_country_id = fields.Many2one(
        "res.country", string="Nazione", ondelete="restrict"
    )
    indirizzo_country_code = fields.Char(
        related="indirizzo_country_id.code", string="Codice Nazione"
    )
    nome_prodotto = fields.Text(string="Nome prodotto")
    codice_prodotto = fields.Text(string="Codice prodotto")
    desc_prodotto = fields.Text(string="Descrizione prodotto")
    qta = fields.Text(string="Quantitá")
    categoria = fields.Text(string="Categoria")
    sottocategoria = fields.Text(string="Sottocategoria")
    larghezza = fields.Text(string="Larghezza")
    altezza = fields.Text(string="Altezza")
    imponibile = fields.Monetary(string="Imponibile", currency_field="valuta")
    codice_imposta = fields.Text(string="Codice Imposta")
    valuta = fields.Many2one(
        "res.currency", string="Valuta", compute="_compute_currency_set_euro"
    )
    totale_fatturato = fields.Monetary(
        string="Fatturato totale", currency_field="valuta"
    )

    @api.depends("totale_fatturato")
    @api.depends("imponibile")
    def _compute_currency_set_euro(self, *args, **kwargs):
        currency = self._get_valuta()
        for record in self:
            record.save_valuta(currency)

    @api.model
    def create(self, vals):
        res_ids = super(stats_base, self).create(vals)
        res_ids.save_valuta(currency=self._get_valuta())
        return res_ids

    def write(self, vals):
        res = super(stats_base, self).write(vals)
        self.save_valuta(currency=self._get_valuta())
        return res

    def _get_valuta(self):
        if self._context.get("default_currency_id"):
            currency = self._context.get("default_currency_id")
        else:
            currency = self.env.ref("base.EUR").id
        return currency

    def save_valuta(self, currency: int = None, *args, **kwargs):
        if currency is None:
            if self._context.get("default_currency_id"):
                currency = self._context.get("default_currency_id")
            else:
                currency = self.env.ref("base.EUR").id
        if self.valuta is None:
            self.valuta = currency

    def to_dict(self):
        return dict(
            ref_middle=self.ref_middle,
            ref_available=self.ref_available,
            ref_status=self.ref_status,
            seriale_fattura=self.seriale_fattura,
            tipo_doc=self.tipo_doc,
            numero_doc=self.numero_doc,
            data_fattura=self.data_fattura,
            cliente_fatturazione=self.cliente_fatturazione,
            vat=self.vat,
            indirizzo_street=self.indirizzo_street,
            indirizzo_street2=self.indirizzo_street2,
            indirizzo_zip=self.indirizzo_zip,
            indirizzo_city=self.indirizzo_city,
            indirizzo_state_id=self.indirizzo_state_id.id,
            indirizzo_country_id=self.indirizzo_country_id.id,
            indirizzo_country_code=self.indirizzo_country_code,
            nome_prodotto=self.nome_prodotto,
            codice_prodotto=self.codice_prodotto,
            desc_prodotto=self.desc_prodotto,
            qta=self.qta,
            categoria=self.categoria,
            sottocategoria=self.sottocategoria,
            larghezza=self.larghezza,
            altezza=self.altezza,
            imponibile=self.imponibile,
            codice_imposta=self.codice_imposta,
            valuta=self.valuta.id,
            totale_fatturato=self.totale_fatturato,
        )


class extend_product(models.Model):
    _description = "Estende l'entità prodotto."
    _inherit = "product.template"

    na_linkdanea_category = fields.Text(string="Categoria")
    na_linkdanea_subcategory = fields.Text(string="Sottocategoria")
    na_linkdanea_width = fields.Text(string="Larghezza")
    na_linkdanea_height = fields.Text(string="Altezza")

    @classmethod
    def na_linkdanea_read_articoli_detail_category(self, raw: dict) -> dict:
        ref = "na_linkdanea"
        """Mappa la definizione degli articoli, in un dizionario consono. Le chiavi del dizionario, devono coincidere con i parametri del modello che estende il prodotto."""
        buffer: dict = {
            "{}_category".format(ref): raw["nomecategoria"].__str__().strip(),
            "{}_subcategory".format(ref): raw["nomesottocategoria"].__str__().strip(),
            "{}_width".format(ref): raw["extra1"]
            .__str__()
            .strip()
            .lower()
            .replace("base", "")
            .replace("larghezza", "")
            .strip(),
            "{}_height".format(ref): raw["extra2"]
            .__str__()
            .strip()
            .lower()
            .replace("altezza", "")
            .strip(),
        }
        return buffer


class extend_lead(models.Model):
    _description = "Estende l'entità Lead."
    _inherit = "crm.lead"

    na_linkdanea_iddoc = fields.Text(string="IDDoc",index=True)
    na_linkdanea_idrighe = fields.Text(string="IDDocRighe",index=True)
    na_linkdanea_numdoc = fields.Text(string="NumDoc",index=True)
    na_linkdanea_descdoc = fields.Text(string="DescDoc",index=True)

    @classmethod
    def na_linkdanea_read_lead_detail(self, raw: dict) -> dict:
        """Mappa la definizione degli articoli, in un dizionario consono. Le chiavi del dizionario, devono coincidere con i parametri del modello che estende il prodotto."""
        ref = "na_linkdanea"
        buffer: dict = {
            "{}_iddoc".format(ref): raw["keys"]["testata"].__str__().strip(),
            "{}_idrighe".format(ref): ",".join(raw["keys"]["righe"]),
            "{}_numdoc".format(ref): raw["values"]["testata"]["NumDoc"],
            "{}_descdoc".format(ref): raw["values"]["testata"]["DescDoc"],
        }
        buffer["expected_revenue"] = raw["values"]["testata"]["TotNetto"]
        if raw["values"]["testata"]["TipoDoc"] == "Q":
            buffer["stage_id"] = 3
        elif raw["values"]["testata"]["TipoDoc"] == "C":
            buffer["stage_id"] = 4
        return buffer


class extend_move(models.Model):
    _description = "Estende l'entità Move."
    _inherit = "account.move"

    na_linkdanea_iddoc = fields.Text(string="IDDoc")
    na_linkdanea_idrighe = fields.Text(string="IDDocRighe")
    na_linkdanea_numdoc = fields.Text(string="NumDoc")
    na_linkdanea_descdoc = fields.Text(string="DescDoc")
    na_linkdanea_totnetto = fields.Text(string="TotNetto")
    na_linkdanea_stats_ref = fields.Text(string="Ref Stats")

    @classmethod
    def na_linkdanea_read_bill_detail(self, raw: dict) -> dict:
        """Mappa la definizione degli articoli, in un dizionario consono. Le chiavi del dizionario, devono coincidere con i parametri del modello che estende il prodotto."""
        ref = "na_linkdanea"
        buffer: dict = {
            "{}_iddoc".format(ref): raw["keys"]["testata"].__str__().strip(),
            "{}_idrighe".format(ref): ",".join(raw["keys"]["righe"]),
            "{}_numdoc".format(ref): raw["values"]["testata"]["NumDoc"],
            "{}_descdoc".format(ref): raw["values"]["testata"]["DescDoc"],
            "{}_totnetto".format(ref): raw["values"]["testata"]["TotNetto"],
        }
        buffer["invoice_date"] = raw["values"]["testata"]["Data"]
        buffer["name"] = "FATT/EasyFatt/{}".format(raw["values"]["testata"]["NumDoc"])
        return buffer
