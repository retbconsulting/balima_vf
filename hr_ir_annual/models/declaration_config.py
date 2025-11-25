# -*- coding: utf-8 -*-

from odoo import fields, models, api

class IrSituationFamille(models.Model):
    
    _name = "ir.situation.famille"
    _rec_name = 'libelle'
    
    libelle = fields.Char('Nom', required=True)
    code = fields.Char('Code', required=True)
    
    
class IrTauxFrais(models.Model):
    
    _name = "ir.taux.frais"
    _rec_name = 'valeur'
    
    valeur =  fields.Char(string='Nom', required=True)
    code = fields.Char(string='Code', required=True)
    date_debut = fields.Date(string='Date début', required=True)
    date_fin = fields.Date(string='Date fin', required=True)
    
class IrModePaiement(models.Model):
    
    _name = "ir.mode.paiement"
    _rec_name = 'libelle'
    
    libelle = fields.Char(string='Nom', required=True)
    code = fields.Char(string='Code', required=True)
    
class IrVille(models.Model):
    
    _name = "ir.ville"
    _rec_name = 'libelle'
    
    libelle = fields.Char('Nom', required=True)
    code = fields.Char('Code', required=True)

class IrElementExonere(models.Model):
    
    _name = "ir.element.exonere"
    _rec_name = 'libelle'
    
    libelle = fields.Char('Nom', required=True)
    code = fields.Char('Code', required=True)
