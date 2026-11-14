# Condominio360 (Django + SQLite3)

Sistema de gestión de condominios: aportaciones, recibos, gastos y usuarios con roles.

## Arranque (Windows, terminal de Cursor, en la carpeta donde está manage.py)

```
py -m venv venv
venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py makemigrations usuario aportacion recibo gasto
python manage.py migrate
python manage.py cargar_demo
python manage.py runserver
```

Abrir http://127.0.0.1:8000/

| Usuario        | Contraseña        | Rol           |
|----------------|-------------------|---------------|
| administrador  | Admin12345        | Administrador |
| residente1     | Residente12345    | Residente     |
| residente2     | Residente12345    | Residente     |

(Para el panel /admin/ crea un superusuario: `python manage.py createsuperuser`.)

## Datos para la demo
```
python manage.py cargar_demo
python manage.py cargar_historial   # 5 meses de historial para las gráficas y reportes
```

## Perfiles
| Perfil | ¿Tiene cuenta? | Qué puede hacer |
|---|---|---|
| **Visitante / externo** | No | Solo ve la página pública (avisos, reglas, áreas comunes, contacto). No envía ni modifica nada |
| **Residente** | Sí | Modo lectura: sus aportaciones, pagos, recibos y reportes; paga en línea con PayPal |
| **Administrador** | Sí | Gestiona todo, además de los avisos públicos |

## Módulos
- **Finanzas**: panel de inicio con gráficas de balance, **Pagos** (cobranza / mis pagos) y **Reportes** mensuales (pantalla, impresión y CSV).
- **aportacion**: cuotas de cada residente. Admin: CRUD. Residente: solo las suyas.
- **recibo**: se genera al registrar el pago de una aportación. Imprimible.
- **gasto**: gastos del condominio (solo Administrador).
- **usuario**: alta/edición de usuarios, roles (Administrador/Residente) y perfil (depto, teléfono).

## Control de acceso (para la demostración)
1. Sin sesión, abrir /aportaciones/ -> redirige al login.
2. Entrar como residente1: el menú no muestra Gastos ni Usuarios.
3. Como residente1 abrir /gastos/ o /usuarios/ -> 403 (acceso denegado).
4. Como residente1 abrir la aportación de residente2 (cambiar el número en la URL,
   p. ej. /aportaciones/4/) -> 404: no revela que existe (evita IDOR).
5. Como residente1 abrir /recibos/pagar/2/ o /aportaciones/nueva/ -> 403.
6. Entrar como administrador: ve y gestiona todo.

Dónde está implementado: `usuario/permisos.py` (roles y mixins) y los
`get_queryset` filtrados en `aportacion/views.py` y `recibo/views.py`.

## Modo lectura del residente
- La barra muestra "Modo lectura" y el menú solo tiene Inicio, Aportaciones, Pagos, Recibos y Reportes.
- `usuario/middleware.py` rechaza con 403 cualquier POST/PUT/PATCH/DELETE de un no administrador
  (excepto iniciar/cerrar sesión), aunque se intente saltar la interfaz.
- Los datos para pagar (banco, CLABE) se editan en `DATOS_PAGO` de `config/settings.py`.

## Pago en línea con PayPal (modo pruebas / sandbox)
1. Crea una cuenta en https://developer.paypal.com y entra a **Apps & Credentials** (modo *Sandbox*).
2. Crea una app y copia el **Client ID** y el **Secret** (sandbox).
3. En **Sandbox > Accounts** usa la cuenta *Personal* (compradora) para pagar en las pruebas.
4. En la terminal, ANTES de `runserver` (misma terminal):

```
$env:PAYPAL_CLIENT_ID="tu_client_id_sandbox"
$env:PAYPAL_CLIENT_SECRET="tu_secret_sandbox"
python manage.py runserver
```
(Si PayPal rechaza MXN: `$env:PAYPAL_CURRENCY="USD"`.)

Flujo: residente → Pagos → «Pagar con PayPal» → aprueba en PayPal → regresa → el servidor captura,
verifica monto y moneda, crea el recibo y marca la aportación como pagada.

Seguridad: el monto sale de la base de datos; solo se paga la propia aportación; la orden queda ligada
al usuario (`PagoPayPal`); recargar el retorno no cobra dos veces; las credenciales viven en variables de
entorno. Única excepción al modo lectura: `usuario/middleware.py` permite el POST de iniciar el pago.
Pruebas: `python manage.py test recibo usuario`

## Perfil visitante (externo, sin cuenta, SOLO LECTURA)
- Entra a `/` sin iniciar sesión y ve: avisos, reglas para visitantes, áreas comunes y datos de contacto
  (editables en `INFO_CONDOMINIO` de `config/settings.py`).
- No puede registrarse, enviar formularios ni modificar nada: `usuario/middleware.py` rechaza con 403
  cualquier POST/PUT/PATCH/DELETE sin sesión (solo permite iniciar sesión).
- No ve datos de residentes: todo lo demás exige sesión y lo redirige al login.
- El administrador publica y edita los avisos en el menú **Avisos**.
- Pruebas: `python manage.py test visitante`
