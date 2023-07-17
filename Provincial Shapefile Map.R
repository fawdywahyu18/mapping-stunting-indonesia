library(sf)
library(raster)
library(sp)
library(rgdal)

# Load Indonesia Shapefile from GADM for Level-1 and Level-2 Administrative Level
shp1 <- shapefile("~/gadm41_IDN_1.shp")
shp2 <- shapefile("~/gadm41_IDN_2.shp")

# Load GTOPO30 Data
tif1  <- raster("~/gt30e100n40.tif")
tif2  <- raster("~/gt30e060n40.tif")
tif_list <- list(tif1, tif2)

# Merge Both GeoTiff RasterLayer Objects
sum_topo <- do.call(merge, tif_list)

# All oneshot


# Make a Little change for 'Kepulauan Riau' into 'Kepri' to distinguish with 'Riau'
provid <- shp1$NAME_1
kpw    <-  which(provid == "Kepulauan Riau")
provid[kpw] <- "Kepri Province"    # For Kepulauan Riau Province #

kpw    <-  which(shp2$NAME_1 == "Kepulauan Riau")
shp2$NAME_1[kpw] <- "Kepri Province"    # For Kepulauan Riau Province #
# ------------------------ #


path0 <- "E:/RISET/Hibah Kompetensi Doktor/"

for (k in 1:length(provid)){
  m <- which(shp2$NAME_1 == provid[k])
  kabkot <- shp2$NAME_2[m]
  path1  <- paste0(path0,provid[k])
  dir.create(path1)
  
  paste1 <- paste0(paste0(provid[k],"."), "polys")
  assign(paste1,shp2[shp2$NAME_2 %in% kabkot,])
  
  paste2 <- paste0(paste0(provid[k],"."), "extent")
  assign(paste2, extent(get(ls(pattern = paste1))))
  
  paste3 <- paste0(paste0(provid[k],"."), "crop")
  assign(paste3, crop(sum_topo, get(ls(pattern = paste1))))
  
  paste4 <- paste0(paste0(provid[k],"."), "mask")
  assign(paste4, mask(get(ls(pattern = paste3)), get(ls(pattern = paste1))))
  
  #paste5 <- paste0(paste0(provid[k],"."), "SPDF")
  #assign(paste5, as(get(ls(pattern = paste3)), "SpatialPolygonDataFrame"))
  
  # --------------------------------------- #
  paste6 <- paste0(paste0(provid[k], "_"),"shapefile")
  
  writeOGR(get(ls(pattern = paste1)), dsn = path1,
           layer = paste6,
           driver = "ESRI Shapefile")
  
  # Load the png for Altitude Map #
  paste7 <- paste0(paste0(path1,(paste0("/", provid[k])),"Altitude.png"))
  png(paste7, width = 1400, height = 1000, units = "px")
  plot(get(ls(pattern = paste4)))
  dev.off()
  # ---------------------------- #  
  
  # Load the png for Provincial Shapefiles by Province #
  paste8 <- paste0(paste0(path1,(paste0("/", provid[k])),"Polygons.png"))
  png(paste8, width = 1400, height = 1000, units = "px")
  plot(get(ls(pattern = paste1)))
  dev.off()
  # --------------------------- #
}