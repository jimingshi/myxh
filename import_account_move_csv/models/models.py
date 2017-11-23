# -*- coding: utf-8 -*-

import base64
import csv
from openerp import models, fields, api
from datetime import date, datetime
from decimal import Decimal
import sys


class EcritureComptable:
    def __init__(self,row):
        for i in row.keys():
            if i=="DATE":
                j,m,a=row["DATE"].split("/")
                self.DATE=date(int(a),int(m),int(j))
            else:
                setattr(self,i,row[i])
                if i in ["DEBIT","CREDIT"]:
                    setattr(self,i,Decimal(getattr(self,i).replace(",",".")))
class PieceComptable:
    def __init__(self):
        self.ecritures=[]
    def ajoute(self,row):
        self.JAL=row["JAL"]
        self.PCE=row["PCE"]
        ecri=EcritureComptable(row)
        self.ecritures.append(ecri)
    def estBalancee(self):
        total=Decimal(0)
        res=""
        for e in self.ecritures:
            total+=Decimal(e.DEBIT)
            total-=Decimal(e.CREDIT)
            res+=" L: "+str(e.LIBELLE)
            res+=" + "+str(Decimal(e.DEBIT))
            res+=" - "+str(Decimal(e.CREDIT))
        res+=" Total: "+str(total)
        return total==Decimal(0),res

class Import_compt(models.Model):
    _name = 'import_account_move_csv.import_compt'
    nom = fields.Char(string="Name")
    fichier=fields.Binary(string="CSV File")
    message_erreur=fields.Char(string="Error Message",readonly="True")
    dateImport=fields.Datetime(string="Date of import",readonly="True")

    def calculeCodePiece(self,row):
        return row["JAL"]+row["PCE"]

    def importer(self,listePieces,detecteErreur=False):
        for o in listePieces:
            company=self.env.user.company_id
            j=self.env['account.journal'].search([["company_id",'=',company.id],["code","=",o.JAL]])
            if not j:
                self.message_erreur="Couldn't find journal %s in company %s"%(o.JAL,company.name)
               # self.message_erreur="Impossible de trouver le journal %s dans la societe %s"%(o.JAL,company.name)
                return False
            estBalancee,res=o.estBalancee()
            if not estBalancee:
                self.message_erreur="Error, account move %s %s is unbalanced: %s" % (o.JAL,o.PCE,res)
                #self.message_erreur="Erreur, la piece comptable %s %s n'est pas balancee: %s" % (o.JAL,o.PCE,res)
                return False
            if not detecteErreur:
                p=self.env['account.move']
                piece=p.create({
                    "ref" : "Import from %s"%(datetime.now()),
                    "company_id" : company.id,
                    "journal_id" : j.id
                })
            for ecriture in o.ecritures:
                compte=self.env['account.account'].search([["company_id","=",company.id],["code","=",ecriture.COMPTE]])
                if not compte:
                    self.message_erreur="Couldn't find account.account %s in company %s"%(ecriture.COMPTE,company.name)
                    #self.message_erreur="Impossible de trouver le compte %s dans la societe %s"%(ecriture.COMPTE,company.name)
                    return False

                if not detecteErreur:
                    l=self.env['account.move.line']
                    ecr=l.with_context(journal_id=j,check_move_validity=False,line_name=ecriture.LIBELLE).create({
                        "account_id" : compte.id,
                        "date" : ecriture.DATE,
                        "debit" : ecriture.DEBIT,
                        "credit" : ecriture.CREDIT,
                        "move_id" : piece.id,
                        "journal_id" : j.id,
                        "date_maturity": ecriture.DATE,
                        "name" : ecriture.LIBELLE,
                    })
        return True


    @api.one
    def importer_fichier(self):
        try:
            decode=base64.b64decode(self.fichier)
            reader=csv.DictReader(decode.splitlines(),delimiter=',', quotechar='"')
            piecesParCode={}
            for row in reader:
                piecesParCode.setdefault(self.calculeCodePiece(row),PieceComptable()).ajoute(row)
        except :
            self.message_erreur=str(sys.exc_info()[0])+ " Error while reading CSV file. Are the columns DATE	JAL	COMPTE	PCE	LIBELLE	DEBIT	CREDIT \n Is the file comma separated, and the delimiter the double quote? no blank field?"
            #self.message_erreur=str(sys.exc_info()[0])+ " Erreur d'importation du fichier CSV. Etes vous sur que les colonnes sont bien DATE	JAL	COMPTE	PCE	LIBELLE	DEBIT	CREDIT"
            return

        listePieces=piecesParCode.values()
        listePieces.sort(key=lambda piece: piece.ecritures[0].DATE)
        if not self.importer(listePieces,detecteErreur=True):
            return
        if self.importer(listePieces,detecteErreur=False):
            self.message_erreur="IMPORT OK"
            self.dateImport=datetime.now()
        return



