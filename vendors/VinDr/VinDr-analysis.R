## For vendor analysis
baseDir  <- '/media/eloygarcia/Almacen HDD/physionet.org/files/vindr-mammo/1.0.0'
VinDr.metadata <- read.csv(file.path(baseDir, 'metadata.csv'), stringsAsFactors = T)
# VinDr.2 <- VinDr.metadata[,7:ncol(VinDr.metadata)]

# ======================================== COMENTARIOS ==================================
### IMS Gioto tiene múlitpeles valores de Rows y columns
### Pixel.Spacing es omitido porque hay valores en blanco pero, en base, el valor es el mismo que Imager.Pixel.Spacing

VinDr.2 <- subset(VinDr.metadata, select=c('Photometric.Interpretation', 'Imager.Pixel.Spacing', 
                                           'Rescale.Intercept', 'Rescale.Slope', 'Rescale.Type','Window.Center...Width.Explanation',
                                           'Manufacturer','Manufacturer.s.Model.Name'))
VinDr.2 <- unique(VinDr.2)

## EMBED
EMBED.metadata <- read.csv('/media/eloygarcia/Elements/Mammography/[2023] - EMBED/tables/EMBED_OpenData_metadata.csv', stringsAsFactors = T)
# EMBED.metadata <- EMBED.metadata[ EMBED.metadata$FinalImageType=='2D',]
summary(EMBED.metadata)

match_resultado <- round(as.numeric(regmatches(EMBED.metadata$ImagerPixelSpacing, regexpr("[0-9]+\\.[0-9]+", EMBED.metadata$ImagerPixelSpacing)) ),3)
EMBED.metadata$ImagerPixelSpacing <- match_resultado

EMBED <- subset(EMBED.metadata, select = c('Manufacturer', 'ManufacturerModelName',
                                           'ImagerPixelSpacing', #'PixelSpacing',
                                           'PhotometricInterpretation', #'PresentationIntentType',
                                           #'PresentationLUTShape',
                                           'RescaleIntercept','RescaleSlope','RescaleType',
                                           #'WindowCenter','WindowWidth','Rows','Columns',
                                           'VOILUTFunction','WindowCenterWidthExplanation') )
EMBED.2 <- unique(EMBED)
summary(EMBED.2)

EMBED.2[EMBED.2$Manufacturer == 'HOLOGIC, Inc.',]
EMBED.2[EMBED.2$Manufacturer == 'Lorad, A Hologic Company',]
EMBED.2[EMBED.2$Manufacturer == 'FUJIFILM Corporation',]
EMBED.2[EMBED.2$Manufacturer == 'GE HEALTHCARE',]
write.csv( EMBED.2[EMBED.2$Manufacturer == 'GE MEDICAL SYSTEMS',], file='/home/eloygarcia/Escritorio/Mierda/Preprocessing/vendors/VinDr/temporal.csv')


### MAMO-MX
mm.b0 <- read.table('/home/eloygarcia/Escritorio/Mierda/Preprocessing/vendors/Mammo-MX/B0_metadata.csv', sep=';', header=T, stringsAsFactors=T)
mm.b1 <- read.table('/home/eloygarcia/Escritorio/Mierda/Preprocessing/vendors/Mammo-MX/B1_metadata.csv', sep=';', header=T, stringsAsFactors=T)

selection <-  c("tag_0008_0070_manufacturer", "tag_0008_1090_manufacturermodelname","tag_0018_1164_imagerpixelspacing",
                "tag_0028_0004_photometricinterpretation",
                "tag_0028_0010_rows","tag_0028_0011_columns","tag_0028_0030_pixelspacing","tag_0028_0100_bitsallocated","tag_0028_0101_bitsstored","tag_0028_0102_highbit","tag_0028_0103_pixelrepresentation","tag_0028_0120_pixelpaddingvalue","tag_0028_0300_qualitycontrolimage",
                "tag_0028_1050_windowcenter","tag_0028_1051_windowwidth","tag_0028_1052_rescaleintercept",
                "tag_0028_1053_rescaleslope","tag_0028_1054_rescaletype",
                "tag_0028_2110_lossyimagecompression","tag_2050_0020_presentationlutshape")

b0<- subset(mm.b0, select=selection)
b1<- subset(mm.b1, select=selection)
