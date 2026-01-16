UserExtend
 └── UserProfile
 └── Address

Catalog
 └── Category
 └── Product ──< ProductImage
               └──< ProductAttributeValue

Cart
 └── Cart ──< CartItem

Orders
 └── Order ──< OrderItem
              └──< OrderStatusHistory

Payments
 └── Payment

Reviews
 └── Review ──< ReviewImage

Inventory
 └── Stock ──< StockMovement

Shipping
 └── ShippingMethod
 └── ShipmentTracking
