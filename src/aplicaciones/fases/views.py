from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse
from django.template.context import RequestContext
from forms import FaseNuevaForm, FaseModificadaForm, FaseModificadaFormProyectoActivo
from .models import Fases
from aplicaciones.proyectos.models import Proyectos
from datetime import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q

# Create your views here.
@login_required(login_url='/login/')
@permission_required('fases.administrar_fases',raise_exception=True)
def adm_fases(request, id_proyecto):
    
    """ Recibe un request, se verifica cual es el usuario registrado y el proyecto del cual se solicita,
    se obtiene la lista de fases con las que estan relacionados el usuario y el proyecto 
    desplegandola en pantalla, ademas permite realizar busquedas avanzadas sobre
    las fases que puede mostrar.
    
    @type request: django.http.HttpRequest.
    @param request: Contiene informacion sobre la solicitud web actual que llamo a esta vista.
    
    @rtype: django.shortcuts.render_to_response.
    @return: fases.html, donde se listan las fases, ademas de las funcionalidades para cada fase.
    
    @author:Romina Diaz de Bedoya.
    
    """
    
    fases = Fases.objects.filter(proyecto=id_proyecto, is_active=True)
    busqueda = ''
    error=False
    if 'busqueda' in request.GET:
        busqueda = request.GET.get('busqueda', '')
        if busqueda:
            qset = (
                Q(nombre__icontains=busqueda) |
                Q(estado__icontains=busqueda) |
                Q(fechainicio__icontains=busqueda) |
                Q(duracion__icontains=busqueda) 
            )
            fases= Fases.objects.filter(qset).distinct()
            if not fases:
                error = True
    proyecto = Proyectos.objects.get(id=id_proyecto)    
    ctx = {'lista_fases':fases, 'query':busqueda, 'error':error, 'id_proyecto':id_proyecto, 'proyecto':proyecto}
    template_name = './Fases/fases.html'
    return render_to_response(template_name, ctx, context_instance=RequestContext(request))

@login_required(login_url='/login/')
@permission_required('fases.add_fases',raise_exception=True)
def crear_fase(request, id_proyecto):
    """ Recibe un request, se verifica si el usuario tiene permisos para crear una fase 
    y se lo redirige a una pagina para que rellene el formulario de creacion de fase,
    una vez completado de forma correcta dicho formulario la fase puede ser creada.
    
    @type request: django.http.HttpRequest.
    @param request: Contiene informacion sobre la solicitud web actual que llamo a esta vista crear_fase.
    
    @rtype: django.shortcuts.render_to_response.
    @return: crearfase.html, donde se encuentra el formulario de creacion de fase y luego a fasealerta.html
    donde se notifica la creacion correcta de la fase.
    
    @author:Romina Diaz de Bedoya.
    
    """
    proyecto = Proyectos.objects.get(id=id_proyecto)
    if proyecto.estado != 'Inactivo':
        mensaje = 'Ya se esta trabajando en el proyecto, no se pueden agregar fases'
        ctx = {'mensaje':mensaje, 'id_proyecto': id_proyecto}
        template_name = 'Fases/fasealerta.html'
        return render_to_response(template_name, ctx, context_instance=RequestContext(request))
    if request.method == 'POST':
        form = FaseNuevaForm(request.POST)
        if form.is_valid():
            nombre_crear = form.cleaned_data['Nombre_de_Fase']
            descripcion = form.cleaned_data['Descripcion']
            duracion = form.cleaned_data['Duracion_semanas']
            mismo_nombre = Fases.objects.filter(nombre=nombre_crear, is_active=True, proyecto_id=id_proyecto)
            
            fase = Fases()
            fase.nombre=nombre_crear
            fase.descripcion=descripcion
            fase.estado='DF'
            fase.fechainicio= datetime.now()
            fase.duracion = duracion
            fase.proyecto_id = id_proyecto
            fase.is_active = True
            
            if (mismo_nombre):
                mensaje = 'El nombre de fase ya existe'
                data ={'Nombre_de_Fase': nombre_crear, 'Descripcion':descripcion, 'Duracion_semanas':duracion}   
                form = FaseNuevaForm(data)
                ctx = {'form': form, 'mensaje':mensaje, 'id_proyecto': id_proyecto}
                template_name = 'Fases/fasenueva.html'
                return render_to_response(template_name, ctx, context_instance=RequestContext(request))
            
            fase.save()
      
            template_name='./Fases/fasecreada.html'
            return render(request, template_name, {'id_proyecto': id_proyecto})
    else: 
        form = FaseNuevaForm()    
        
    template_name='./Fases/fasenueva.html'
    return render(request, template_name, {'form': form, 'id_proyecto':id_proyecto})

@login_required(login_url='/login/')
def consultar_fase (request, id_fase, id_proyecto):
    
    """ Recibe un request y el id de la fase a ser consultada, se verifica si el usuario tiene
    permisos para consultar una fase y se lo redirige a una pagina que despliega los datos de la
    fase solicitado.
    
    @type request: django.http.HttpRequest.
    @param request: Contiene informacion sobre la solicitud web actual que llamo a esta vista consultar_fase.
     
    @rtype: django.shortcuts.render_to_response.
    @return: consultarfase.html, donde se encuentra la pagina de consulta de fase.
    
    @type id_usuario : string.
    @param id_usuario : Contiene el id de la fase a ser consultada.
    
    @author:Romina Diaz de Bedoya.
    
    """
    
    fase = Fases.objects.get(id=id_fase, proyecto_id=id_proyecto)
    # conseguir el contexto de las fases y sus estados
    #fases = Fases.objects.filter(id_proyecto = id_proyecto)
    ctx = {'fase':fase}
    template_name = './Fases/consultarfase.html'
    return render(request, template_name, {'id_proyecto': id_proyecto, 'fase': fase, 'id_fase': id_fase})
    
@login_required(login_url='/login/')
@permission_required('fases.delete_fases',raise_exception=True)
def eliminar_fase (request, id_fase, id_proyecto):
    
    """ Recibe un request y el id de la fase a ser eliminada, se verifica si el usuario tiene
    permisos para eliminar una fase existente y le brinda la opcion de eliminar la fase.
    
    @type request: django.http.HttpRequest.
    @param request: Contiene informacion sobre la solicitud web actual que llamo a esta vista eliminar_fase.
     
    @rtype: django.shortcuts.render_to_response.
    @return: adm_fases.html, donde se redirige al usuario con actualizacion de la lista de fases o a
    fasealerta.html donde se notifica al usuario la razon por la cual no se puede eliminar la fase.
    
    @type id_usuario : string.
    @param id_usuario : Contiene el id de la fase a ser eliminada.
    
    @author:Romina Diaz de Bedoya.
    
    """
    
    fase = Fases.objects.get(id=id_fase, proyecto_id=id_proyecto)
    proyecto = Proyectos.objects.get(id=id_proyecto)
    if (proyecto.estado != 'Inactivo'):
        mensaje = 'Imposible eliminar la fase, ya se esta trabajando en el proyecto.'
        ctx = {'mensaje':mensaje, 'id_proyecto': id_proyecto}
        template_name = 'Fases/fasealerta.html'
        return render_to_response(template_name, ctx, context_instance=RequestContext(request))
    
    else:
        fase.is_active = False
        nom = fase.nombre
        fase.nombre_eliminado = fase.nombre
        fase.nombre = '/eliminado/'+fase.nombre_eliminado
        fase.save()
        template_name='./Fases/faseeliminada.html'
        return render(request, template_name, {'id_proyecto': id_proyecto})

@login_required(login_url='/login/')
@permission_required('fases.change_fases',raise_exception=True)
def modificar_fase (request, id_proyecto, id_fase):
    
    """ Recibe un request y el id de la fase a ser modificada, se verifica si el usuario tiene
    permisos para modificar una fase existente y se lo redirige a una pagina para que modifique el 
    formulario existente de una fase, una vez modificado de forma correcta dicho formulario la fase
    puede ser modificada.
    
    @type request: django.http.HttpRequest.
    @param request: Contiene informacion sobre la solicitud web actual que llamo a esta vista crear_fase.
     
    @rtype: django.shortcuts.render_to_response.
    @return: modificarfase.html, donde se encuentra el formulario de modificacion de fase y luego a 
    fasealerta.html donde se notifica la modificacion correcta de una fase.
    
    @type id_usuario : string.
    @param id_usuario : Contiene el id de la fase a ser modificada.
    
    @author:Romina Diaz de Bedoya.
    
    """
    proyecto = Proyectos.objects.get(id=id_proyecto) 
    fase = Fases.objects.get(id=id_fase, proyecto_id=id_proyecto)
    mensaje=''
    if request.method == 'POST':
        if proyecto.estado == 'Inactivo': 
            form = FaseModificadaForm(request.POST)
            if form.is_valid():
                form.clean()
                nombreNuevo = form.cleaned_data['Nombre_de_Fase'] 
                descripcionNueva =  form.cleaned_data['Descripcion']
                estadoNuevo = form.cleaned_data['Estado']
                duracionNueva =  form.cleaned_data['Duracion']
                mismo_nombres = Fases.objects.filter(nombre=nombreNuevo, is_active=True, proyecto_id=id_proyecto)
                repetido='Vacio'
                    
                if (mismo_nombres):
                    for nombre in mismo_nombres:
                        if (nombre.id!=fase.id):
                            repetido='No'
                    
                if (repetido=='No'):
                    mensaje = 'El nombre de Fase ya existe'
                    data ={'Nombre_de_Fase':fase.nombre, 'Descripcion':fase.descripcion, 'Estado':fase.estado, 'Duracion':fase.duracion}
                    form = FaseModificadaForm(data)
                    ctx ={'form': form, 'mensaje':mensaje, 'id_proyecto':id_proyecto, 'id_fase':id_fase}      
                    template_name='Fases/modificarfase.html'
                    return render_to_response(template_name, ctx, context_instance=RequestContext(request))
                     #Si no se ha suministrado un nuevo lider, el proyecto se queda con el lider actual
                if nombreNuevo:
                    fase.nombre = nombreNuevo
                if descripcionNueva:
                    fase.descripcion = descripcionNueva
                if duracionNueva:
                    fase.duracion = duracionNueva
                if estadoNuevo:
                    if (estadoNuevo=='DR') or (estadoNuevo=='FD'):
                        mensaje = 'No se puede modificar el estado sin items'
                        data ={'Nombre_de_Fase':fase.nombre, 'Descripcion':fase.descripcion, 'Estado':fase.estado, 'Duracion':fase.duracion}
                        form = FaseModificadaForm(data)
                        ctx ={'form': form, 'mensaje':mensaje, 'id_proyecto':id_proyecto, 'id_fase':id_fase}      
                        template_name='Fases/modificarfase.html'
                        return render_to_response(template_name, ctx, context_instance=RequestContext(request))
                    else:
                        fase.estado = estadoNuevo
                fase.save()
                mensaje="Fase modificada exitosamente"
                ctx = {'mensaje':mensaje, 'id_proyecto': id_proyecto, 'id_fase':id_fase}
                template_name='Fases/fasealerta.html'
                return render_to_response(template_name, ctx, context_instance=RequestContext(request))
            else:
                data ={'Nombre_de_Fase':fase.nombre, 'Descripcion':fase.descripcion, 'Estado':fase.estado, 'Duracion':fase.duracion}   
                form = FaseModificadaForm(data)
            ctx ={'form': form, 'mensaje':mensaje, 'id_proyecto':id_proyecto, 'id_fase':id_fase}      
            template_name='Fases/modificarfase.html'
            return render_to_response(template_name, ctx, context_instance=RequestContext(request))
        
        elif proyecto.estado=='En Construccion':
            if (fase.estado=='FD'):
                mensaje = 'No se puede modificar la fase, ha finalizado.'
                ctx ={'mensaje':mensaje, 'id_proyecto':id_proyecto, 'id_fase':id_fase}      
                template_name='Fases/fasealerta.html'
                return render_to_response(template_name, ctx, context_instance=RequestContext(request))
            form = FaseModificadaFormProyectoActivo(request.POST)
            if form.is_valid():
                form.clean()
                estadoNuevo = form.cleaned_data['Estado']
                duracionNueva =  form.cleaned_data['Duracion']
                estadoActual = fase.estado
                duracionActual = fase.duracion
                if (duracionNueva):
                    duracion = duracionNueva
                else:
                    duracion = fase.duracion
                if (estadoNuevo):
                    if (estadoActual=='DF' and estadoNuevo!='DF'):
                        mensaje = 'No se puede modificar el estado de la fase, aun no posee items.'
                        data ={'Estado':fase.estado, 'Duracion':duracion}
                        form = FaseModificadaFormProyectoActivo(data)
                        ctx ={'form': form, 'mensaje':mensaje, 'id_proyecto':id_proyecto, 'id_fase':id_fase}      
                        template_name='Fases/modificarfase.html'
                        return render_to_response(template_name, ctx, context_instance=RequestContext(request))
                    elif estadoActual=='DF':
                        fase.duracion=duracion
                        fase.save()
                        mensaje = 'Fase editada con exito'
                        ctx ={'mensaje':mensaje, 'id_proyecto':id_proyecto, 'id_fase':id_fase}      
                        template_name='Fases/fasealerta.html'
                        return render_to_response(template_name, ctx, context_instance=RequestContext(request))
                    elif (estadoActual=='DR' and estadoNuevo=='DF'):
                        mensaje = 'No se puede volver al estado definicion.'
                        data ={'Estado':fase.estado, 'Duracion':duracion}
                        form = FaseModificadaFormProyectoActivo(data)
                        ctx ={'form': form, 'mensaje':mensaje, 'id_proyecto':id_proyecto, 'id_fase':id_fase}      
                        template_name='Fases/modificarfase.html'
                        return render_to_response(template_name, ctx, context_instance=RequestContext(request))
                    elif (estadoActual=='DR' and estadoNuevo=='FD'):
                        mensaje = 'No se puede finalizar la fase. Todos los items deben pertenecer a una Linea Base.'
                        data ={'Estado':fase.estado, 'Duracion':duracion}
                        form = FaseModificadaFormProyectoActivo(data)
                        ctx ={'form': form, 'mensaje':mensaje, 'id_proyecto':id_proyecto, 'id_fase':id_fase}      
                        template_name='Fases/modificarfase.html'
                        return render_to_response(template_name, ctx, context_instance=RequestContext(request))
                    elif (estadoActual=='DR' and estadoNuevo=='DR'):
                        fase.duracion=duracion
                        fase.save()
                        mensaje = 'Fase editada con exito'
                        ctx ={'mensaje':mensaje, 'id_proyecto':id_proyecto, 'id_fase':id_fase}      
                        template_name='Fases/fasealerta.html'
                        return render_to_response(template_name, ctx, context_instance=RequestContext(request))
                else:
                    fase.duracion = duracion
                    fase.save()
                    mensaje = 'Fase editada con exito'
                    ctx ={'mensaje':mensaje, 'id_proyecto':id_proyecto, 'id_fase':id_fase}      
                    template_name='Fases/fasealerta.html'
                    return render_to_response(template_name, ctx, context_instance=RequestContext(request))
            else:
                data ={'Estado':fase.estado, 'Duracion':fase.duracion}   
                form = FaseModificadaFormProyectoActivo(data)
                ctx ={'form': form, 'mensaje':mensaje, 'id_proyecto':id_proyecto, 'id_fase':id_fase}      
                template_name='Fases/modificarfase.html'
                return render_to_response(template_name, ctx, context_instance=RequestContext(request))
    elif proyecto.estado=='Inactivo':
        data ={'Nombre_de_Fase':fase.nombre, 'Descripcion':fase.descripcion, 'Estado':fase.estado, 'Duracion':fase.duracion}
        form = FaseModificadaForm(data)
    elif proyecto.estado=='En Construccion':
        data ={'Estado':fase.estado, 'Duracion':fase.duracion}
        form = FaseModificadaFormProyectoActivo(data)
    elif proyecto.estado=='Finalizado':
        mensaje = 'La fase no se puede modificar, el proyectos esta finalizado.'
        ctx ={'mensaje':mensaje, 'id_proyecto':id_proyecto, 'id_fase':id_fase}      
        template_name='Fases/fasealerta.html'
        return render_to_response(template_name, ctx, context_instance=RequestContext(request))
    
    ctx ={'form': form, 'mensaje':mensaje, 'id_proyecto':id_proyecto, 'id_fase':id_fase}
    template_name='Fases/modificarfase.html'
    return render_to_response(template_name, ctx, context_instance=RequestContext(request))
    
    
@login_required(login_url='/login/')
@permission_required('fases.importar_fase',raise_exception=True)
def importar_fase (request, id_proyecto):
    
    """ Recibe un request, se verifica los permisos del usuario que desea importar una fase y luego se lo 
    redirige a la pagina donde se lista las fases del sistema que pueden ser importadas.
  
    @type request: django.http.HttpRequest.
    @param request: Contiene informacion sobre la solicitud web actual que llamo a esta vista importar_fase.
    
    @rtype: django.shortcuts.render_to_response.
    @return: importarfase.html, donde se encuentra la pagina que lista las fases a ser importadas.
    
    @author:Romina Diaz de Bedoya.
    
    """
    proyecto = Proyectos.objects.get(id=id_proyecto)
    if proyecto.estado != 'Inactivo':
        mensaje = 'Ya se esta trabajando en el proyecto, no se pueden agregar fases'
        ctx = {'mensaje':mensaje, 'id_proyecto': id_proyecto}
        template_name = 'Fases/fasealerta.html'
        return render_to_response(template_name, ctx, context_instance=RequestContext(request))
    fases = Fases.objects.filter(is_active=True)
    lista_proyectos = []
    for fase in fases:
        proyec = Proyectos.objects.filter(id=fase.proyecto_id)
        lista_proyectos.extend(proyec)
    ctx ={'lista_fases':fases, 'lista_proyectos':lista_proyectos, 'id_proyecto': id_proyecto}
    template_name = 'Fases/importarfase.html'
    return render_to_response(template_name, ctx, context_instance=RequestContext(request))


@login_required(login_url='/login/')
def importarf (request, id_proyecto, id_fase):
    
    """ Recibe un request y el id de la fase a ser importada, se verifica si el usuario tiene
    permisos para importar una fase existente, luego se lo redirige a la pagina para completar los
    datos del formulario de nueva fase importada, una vez completado correctamente el formulario el
    sistema crea una nueva fase con las caracteristicas de la fase importada.
    
    @type request: django.http.HttpRequest.
    @param request: Contiene informacion sobre la solicitud web actual que llamo a esta vista importar.
     
    @type id_usuario : string.
    @param id_usuario : Contiene el id del proyecto a ser importado.
    
    @rtype: django.shortcuts.render_to_response.
    @return: crearfaseimportada.html, donde se redirige al usuario para completar los datos de la nueva
    fase importada o a fasealerta.html donde se notifica que la fase fue importada correctamente.
    
    @author:Romina Diaz de Bedoya.
    
    """
    
    faseImportada = Fases.objects.get(id=id_fase)
    if request.method == 'POST':
        form = FaseModificadaForm(request.POST)
        if form.is_valid():
            form.clean()
            nombre = form.cleaned_data['Nombre_de_Fase']
            descripcion = form.cleaned_data['Descripcion']
            duracion = form.cleaned_data['Duracion']
            mismo_nombre = Fases.objects.filter(nombre=nombre, is_active=True, proyecto_id=id_proyecto)
            
            fase = Fases()
            fase.nombre=nombre
            fase.descripcion=descripcion
            fase.estado='DF'
            fase.fechainicio= datetime.now()
            fase.duracion = duracion
            fase.proyecto_id = id_proyecto
            fase.is_active = True
            
            repetido=False
            for mismos_nombre in mismo_nombre:
                if (mismos_nombre.id!=id_fase):
                    repetido=True
            
            if (repetido):
                mensaje = 'El nombre de Fase ya existe'
                data ={'Nombre_de_Fase':fase.nombre, 'Descripcion':fase.descripcion, 'Estado':fase.estado, 'Duracion':fase.duracion}
                form = FaseModificadaForm(data)
                ctx ={'form': form, 'mensaje':mensaje, 'id_proyecto':id_proyecto, 'id_fase':id_fase}      
                template_name='Fases/crearfaseimportada.html'
                return render_to_response(template_name, ctx, context_instance=RequestContext(request))
            
            fase.save()
                
            mensaje="Fase importada exitosamente"
            ctx = {'mensaje':mensaje, 'id_proyecto':id_proyecto}
            return render_to_response('Fases/fasealerta.html',ctx, context_instance=RequestContext(request))
    else:
        data ={'Nombre_de_Fase':faseImportada.nombre, 'Descripcion':faseImportada.descripcion, 'Estado':faseImportada.estado, 'Duracion':faseImportada.duracion}   
        form = FaseModificadaForm(data)
        
    ctx ={'form': form, 'fase':faseImportada}
    template_name='Fases/crearfaseimportada.html'
    return render_to_response(template_name, ctx, context_instance=RequestContext(request))

