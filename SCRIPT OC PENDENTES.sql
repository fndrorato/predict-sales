SELECT *
FROM pegasus.dbo.view_powerbi_recepcion_mercaderias as r
WHERE r.nro_pedido = 325272
ORDER BY r.nro_pedido DESC;


SELECT NRO_OC, FECHA, ABIERTA, COD_SUCURSAL, nombre_sucursal, cod_proveedor, nombre_proveedor, tipo_documen, tipo_descripcion, cod_condicion, CONDICION, COD_PLAZO, PLAZO, FECHA_ENTREGA, estado, cod_rubro, descripcion, importe, observacion, edi, observacion_prob, aut, fec_recep, codigo, descripcion_producto, cantidad, precio
FROM pegasus.dbo.view_powerbi_OC as oc
WHERE oc.NRO_OC = 325288;

SELECT *
FROM pegasus.dbo.view_powerbi_OC as oc
WHERE oc.NRO_OC = 325288;

SELECT 	ocfe.COD_SUCURSAL  as sucursal, r.nro_pedido, ocfe.importe, ocfe.ABIERTA  as abierta, 
		r.fecha, ocfe.FECHA_ENTREGA  as fecha_prevista, ocfe.fec_recep  as fecha_recepcion,
		r.cod_proveedor, r.codigo,  r.cantidad_ped, r.cantidad_recep, ocfe.precio
FROM pegasus.dbo.view_powerbi_recepcion_mercaderias as r,
(
	SELECT DISTINCT NRO_OC, COD_SUCURSAL, FECHA_ENTREGA, ABIERTA, fec_recep, importe, codigo, precio
	FROM pegasus.dbo.view_powerbi_OC as oc
) as ocfe
WHERE r.fecha >= '2025-01-01'
AND r.nro_pedido = ocfe.NRO_OC
AND r.codigo = ocfe.codigo
ORDER BY r.nro_pedido DESC;
