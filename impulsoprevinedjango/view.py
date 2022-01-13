# -*- encoding:utf-8 -*-
# Usado para encontrar urls
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView
from .formulario import DadosBanco
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from pandas.io import sql
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt


def readQuery(query):
    database = 'impulsogov-analitico'
    credencial = json.load(open('credencial.json'))
    engine = create_engine(
      'postgresql://{}:{}@{}:{}/{}?'.format(credencial[database][0]['USERNAME'],
                        credencial[database][0]['PASSWORD'],
                        credencial[database][0]['HOSTNAME'],
                        credencial[database][0]['PORT'],
                        credencial[database][0]['DATABASE']), connect_args={"options": "-c statement_timeout=100000000"}
    )
    conexao = engine.connect()
    resultados = sql.read_sql(query, conexao)
    return resultados


class Inicio(TemplateView):
    template_name = 'inicio.html'

class Impulso(TemplateView):
    template_name = 'impulso.html'

class Guias(TemplateView):
    template_name = 'guias.html'

class Paineis(TemplateView):
    template_name = 'paineis.html'

class Login(TemplateView):
    template_name = 'login.html'

class Perfil(TemplateView): # new
    template_name = 'perfil.html'

    def get_context_data(self, **kwargs):
        context = super(Perfil, self).get_context_data(**kwargs)
        context['url'] = "https://sites.google.com/impulsogov.org/agpsaude-teste/inicio/"+context['municipio']
        return context

class DadosAdm(TemplateView): # new
    form_class = DadosBanco
    template_name = 'dados.html'

    def get_context_data(self, **kwargs):
        context = super(DadosAdm, self).get_context_data(**kwargs)
        context['form'] = DadosBanco()
        context['botao_avancar'] = reverse("dados")
        return context
    
    # def post(self, request, *args, **kwargs):
    #     import pdb; pdb.set_trace()
    #     body = {
    #         "name" : request.POST["name"],
    #         "tag_name" : remove_accents(request.POST["tag_name"]),
    #         "segment_id" : request.POST["segment_id"],
    #         "send_order" : request.POST["send_order"],
    #         "config_id": request.POST["config"],
    #         "company_id": Company.objects.filter(name=self.kwargs['account_name'])[0].pk,
    #         "deleted_flag" : False
    #     }
    #     return HttpResponseRedirect(reverse_lazy("graficos"))

    # def dispatch(self, *args, **kwargs):
    #     return super(DadosAdm, self).dispatch(*args, **kwargs)




class Graficos(TemplateView):
    template_name = 'graficos.html'

    def get_context_data(self, **kwargs):
        context = super(Graficos, self).get_context_data(**kwargs)
        query_piraju = """
        SELECT
            t3.no_unidade_saude,
            t3.no_equipe,
            t3.nu_micro_area,	
            t3.st_gestante,
            t3.st_hipertensao_arterial,
            t3.st_diabete
            FROM
            (
                SELECT
                    t2.*,
                    tb_dim_unidade_saude.nu_cnes,
                    tb_dim_unidade_saude.no_unidade_saude
                FROM
                (
                    SELECT 
                        t1.*,
                        tb_dim_equipe.nu_ine,
                        tb_dim_equipe.no_equipe
                    FROM
                    (
                        SELECT
                            CASE WHEN nu_cns IS NULL THEN '0'
                            ELSE nu_cns END
                            nu_cns,
                        co_dim_unidade_saude,
                        co_dim_equipe,
                        co_dim_sexo,
                        CASE WHEN nu_micro_area IS NULL THEN '00'
                            ELSE nu_micro_area END
                            nu_micro_area,
                        st_ficha_inativa,
                        CASE WHEN st_gestante IS NULL THEN '0'
                            ELSE st_gestante END
                            st_gestante,
                        CASE WHEN st_hipertensao_arterial IS NULL THEN '0'
                            ELSE st_hipertensao_arterial END
                            st_hipertensao_arterial,
                        CASE WHEN st_diabete IS NULL THEN '0'
                            ELSE st_diabete END
                            st_diabete
                    FROM 
                        tb_fat_cad_individual 
                    ORDER BY co_dim_tempo DESC
                    ) AS t1
                    LEFT JOIN
                        tb_dim_equipe
                    ON tb_dim_equipe.co_seq_dim_equipe = t1.co_dim_equipe
                ) AS t2
                LEFT JOIN
                    tb_dim_unidade_saude
                ON tb_dim_unidade_saude.co_seq_dim_unidade_saude = t2.co_dim_unidade_saude
            ) AS t3
            limit 800
        """
        df = readQuery(query_piraju)
        context['dados'] = json.loads(df.to_json(orient='records'))
        return context