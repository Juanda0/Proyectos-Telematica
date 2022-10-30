# PIBL project


## I. Introducción.

Este proyecto consta del desarrollo de un servidor que implementa un proxy inverso y un balanceador de carga con el objetivo de redirigir las peticiones http a 3 distintos servidores y reducir el estres en estos.

## II. Desarrollo

### Lenguaje
El lenguaje escogido para el desarrollo del PIBL fue Python, esto debido a que -- inserte argumentos --. Asi mismo, los diferentes servidores web tambien fueron desarrollados en Python. 

### Servidores
Los servidores escogidos corren en Ubuntu - linux y se encuentran en la cloud AWS. En el archivo config.py se encuentra la pool de direcciones ip parametrizable para poner todas las direcciones de estos

### Infraestructura
Mediante el uso de API sockets se monto la infraestructura necesaria para la comunicacion del cliente con el servidor PIBL y la comunicacion de este mismo con los servidores web. La Infraestructura cuenta con 1 socket escuchando constantemente en el puerto 8080 (parametrizable) en el servidor PIBL las peticiones de los clientes y adicionalmente 1 socket extra por servidor (en este caso 3) que escuchan constantemente en otro puerto parametrizable las peticiones realizadas por el PIBL. En este orden de ideas la peticion de un usuario se veria de la forma cliente -> PIBL -> servidor n, donde > representa la ubicacion respectiva de cada socket. Finalmente, los parametros para enlazar en el socket deseado son proporcionados gracias a la estrategia de balanceo de carga, que siempre retorna un servidor disponible

### Balanceador de carga
Para el balanceo de cargas es necesario el uso de una politica que permita al programa escoger el servidor disponible mas optimo. Para efectos de la practica la politica usada en el balanceador de carga fue Round Robin, que distribuye de manera equivalente todas las peticiones realizadas por los usuarios.

### Cache
Se implementó una estrategia de caching con el objetivo de evitar peticiones reduntantes. Para esto, se almacenó el recurso solicitado junto a su metodo como una llave, para posteriormente almacenar el recurso retornado como la value en un archivo local. Al ser necesaria una estrategia para validar si el recurso es lo suficientemente actual, se implementó TTL basado en estampas de tiempo. Se mira el tiempo que ha pasado desde que se almaceno el recurso y se compara con un parametro arbitrario TTL, si el recurso aun esta dentro del rango de tiempo, es retornado.

## III. Conclusiones
El desarrollo de una infraestructura capaz de soportar peticiones concurrentes de decenas de personas puede ser algo demasiado complejo si se tratase de solucionar mediante una escalacion vertical. Caso contrario al escalamiento horizontal, que mediante el uso de intermediarios como el PIBL permite incluir diversas maquinas a la infraestructura, dando lugar a la gestion de estas y asi facilitando el acceso a miles de usuarios con un menor costo y mayor versatilidad.

## IV. Referencias
/buscar articulos sobre las ventajas de Round robin, python y escalamiento vertical
