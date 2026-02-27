/* SQL DE VENDAS */
SELECT bcv.nro_reg, bcv.fecha, bcv.hora, bcv.nro_factura, bcv.cod_sucursal, bcv.codigo, bcv.cant_vta, bcv.ventas_det_precio_neto 
FROM pegasus.dbo.bi_compra_venta AS bcv
WHERE bcv.tipo = 'VENTA'
and bcv.fecha  >= '2025-08-01'
and bcv.fecha <= '2025-08-17'
ORDER BY bcv.fecha DESC;

/* bi_proveedores */
SELECT * FROM bi_proveedores;

/* PRODUCTOS */
SELECT codigo, descripcion_producto, cant_paq, cant_min, unidad, precio_compra, precio_costo, tipo_fiscal, imp_imp, servicio, nivel1, nivel2, nivel3, nivel4, nivel5, marca, precio_vta, codigo_barra, Desactivado_compra, desactivar_web, DESACTIVADO, POS, desactivo_pgs, critico, PERECEDERO, COMPUESTO, Produccion, Seguro, descuento_NC, Percha, fleje, etiqueta, pesable, serie, interes, bar_patio, mcc, restring, comanda, bonificacion_mobile, cod_proveedor_principal, proveedor_principal, precio_matriz
FROM pegasus.dbo.bi_productos;

/* STOCK */
SELECT codigo, cod_sucursal, cod_deposito, cantidad
FROM pegasus.dbo.bi_stock;
