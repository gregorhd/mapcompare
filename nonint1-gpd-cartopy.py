"""Figure Ideas...

    # Example: Three equivalent plotting syntaxes wih GPD and cartopy

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, subplot_kw={'projection': crs}, figsize=(20, 10))

    fig.tight_layout(pad=3)

    fontsize = 18

    # Plot directly with GeoPandas

    ax1.set_extent(carto_extent, crs=crs)
    ax1.set_title("GeoPandas: GDF.plot(ax=ax, *kwargs)" + "\n", fontsize=fontsize)
    
    buildings_in.plot(ax=ax1, facecolor='red')

    buildings_out.plot(ax=ax1, facecolor='white', edgecolor='black', linewidth=0.1)

    rivers.plot(ax=ax1, facecolor='lightblue')

    # Cartopy Syntax 1: GDF to ShapelyFeature, then add_feature

    ax2.set_extent(carto_extent, crs=crs)
    ax2.set_title("Cartopy 1: feat = ShapelyFeature(GDF.geometry, crs, *kwargs)" + "\n" + "ax.add_feature(feat)", fontsize=fontsize)

    buildings_in_feat = ShapelyFeature(buildings_in.geometry, crs, facecolor='red')
    ax2.add_feature(buildings_in_feat)

    buildings_out_feat = ShapelyFeature(buildings_out.geometry, crs, facecolor='white', edgecolor='black', linewidth=0.1)
    ax2.add_feature(buildings_out_feat)

    rivers_feat = ShapelyFeature(rivers.geometry, crs, facecolor='lightblue')
    ax2.add_feature(rivers_feat)

    # Cartopy Syntax 2: add_geometries + basemap

    ax3.set_title("Cartopy 2: ax.add_geometries(GDF.geometry, crs=crs, *kwargs)", fontsize=fontsize)
    ax3.set_extent(carto_extent, crs=crs)

    ax3.add_geometries(buildings_in.geometry, crs=crs, facecolor='red')

    ax3.add_geometries(buildings_out.geometry, crs=crs, facecolor='white', edgecolor='black', linewidth=0.1)

    ax3.add_geometries(rivers.geometry, crs=crs, facecolor='lightblue')

    # Cartopy add_geometries + basemap

    ax4.set_title("Cartopy add_geometries + contextily basemap", fontsize=fontsize)
    ax4.set_extent(carto_extent, crs=crs)

    ax4.add_geometries(buildings_in.geometry, crs=crs, facecolor='red')

    ax4.add_geometries(buildings_out.geometry, crs=crs, facecolor='white', edgecolor='black', linewidth=0.1)

    ax4.add_geometries(rivers.geometry, crs=crs, facecolor='lightblue')

    ctx.add_basemap(ax4, crs=buildings_in.crs.to_string(), source=ctx.providers.Esri.WorldShadedRelief)

"""
    
    