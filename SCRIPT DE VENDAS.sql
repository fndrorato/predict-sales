SELECT bcv.nro_reg, bcv.fecha, bcv.hora, bcv.nro_factura, bcv.cod_sucursal, bcv.codigo, bcv.cant_vta, bcv.ventas_det_precio_neto 
FROM pegasus.dbo.bi_compra_venta AS bcv
WHERE bcv.tipo = 'VENTA'
and bcv.fecha  >= '2023-01-01'
and bcv.cod_sucursal = 4
ORDER BY bcv.nro_reg  DESC;

SELECT bcv.* 
FROM pegasus.dbo.bi_compra_venta AS bcv
WHERE bcv.tipo = 'VENTA'
AND bcv.fecha  >= '2025-01-01';

SELECT *
FROM pegasus.dbo.bi_compra_venta AS bcv
WHERE bcv.tipo = 'VENTA'
AND bcv.fecha  >= '2025-01-01'
AND (bcv.cod_motivo = 0 OR bcv.cod_motivo IS NOT NULL);

SELECT DISTINCT bcv.cod_motivo, bcv.motivo_descripcion
FROM pegasus.dbo.bi_compra_venta AS bcv
WHERE bcv.tipo = 'VENTA'
AND bcv.fecha  >= '2025-01-01';

SELECT bcv.nro_reg, bcv.fecha, bcv.hora, bcv.nro_factura, bcv.cod_sucursal, bcv.codigo, bcv.cant_vta, bcv.ventas_det_precio_neto 
FROM pegasus.dbo.bi_compra_venta AS bcv
WHERE bcv.tipo = 'VENTA'
and bcv.fecha  >= '2025-08-01'
and bcv.cod_sucursal = 4
ORDER BY bcv.nro_reg  DESC;

