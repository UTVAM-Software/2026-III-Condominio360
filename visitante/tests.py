from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from usuario.forms import asignar_rol

from .models import Aviso

CLAVE = 'Prueba12345'


class VisitanteSoloLecturaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user('adm', password=CLAVE)
        asignar_rol(cls.admin, 'Administrador')
        cls.res = User.objects.create_user('res', password=CLAVE)
        asignar_rol(cls.res, 'Residente')

    def test_visitante_ve_la_pagina_publica_sin_cuenta(self):
        Aviso.objects.create(titulo='Aviso visible', contenido='Hola')
        Aviso.objects.create(titulo='Aviso oculto', contenido='Interno', publicado=False)
        r = self.client.get(reverse('inicio'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Aviso visible')
        self.assertNotContains(r, 'Aviso oculto')
        self.assertContains(r, 'visitante')

    def test_visitante_no_entra_a_zonas_privadas(self):
        for nombre in ('aportacion:lista', 'recibo:lista', 'gasto:lista', 'usuario:lista',
                       'pagos', 'reporte', 'visitante:avisos'):
            r = self.client.get(reverse(nombre))
            self.assertEqual(r.status_code, 302, nombre)
            self.assertIn('/login/', r['Location'], nombre)

    def test_visitante_no_puede_enviar_ni_modificar_nada(self):
        for nombre, args in (('aportacion:crear', []), ('gasto:crear', []),
                             ('usuario:crear', []), ('visitante:aviso_crear', [])):
            r = self.client.post(reverse(nombre, args=args), {'x': 'y'})
            self.assertEqual(r.status_code, 403, nombre)

    def test_visitante_si_puede_iniciar_sesion(self):
        r = self.client.post(reverse('login'), {'username': 'adm', 'password': CLAVE})
        self.assertEqual(r.status_code, 302)

    def test_visitante_no_ve_datos_de_residentes(self):
        r = self.client.get(reverse('inicio'))
        self.assertNotContains(r, 'Pagos')
        self.assertNotContains(r, 'Aportaciones')

    def test_residente_no_gestiona_avisos(self):
        self.client.login(username='res', password=CLAVE)
        self.assertEqual(self.client.get(reverse('visitante:avisos')).status_code, 403)

    def test_admin_gestiona_avisos(self):
        self.client.login(username='adm', password=CLAVE)
        self.assertEqual(self.client.get(reverse('visitante:avisos')).status_code, 200)
        r = self.client.post(reverse('visitante:aviso_crear'),
                             {'titulo': 'Nuevo', 'contenido': 'Texto', 'publicado': 'on'})
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Aviso.objects.filter(titulo='Nuevo').exists())
