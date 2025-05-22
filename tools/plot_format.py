def format_axis_line(g, xtext, ytext):
    xticks = g.axes[0][0].get_xticks()
    xlabels = [xtext.format(x) for x in xticks]
    g.set_xticklabels(xlabels)
    yticks = g.axes[0][0].get_yticks()
    ylabels = [ytext.format(y) for y in yticks]
    g.set_yticklabels(ylabels)
    g.set_xlabels(fontsize=16, fontweight='bold', labelpad=12)
    g.set_xticklabels(fontsize=14)
    g.set_ylabels(fontsize=16, fontweight='bold', labelpad=12)
    g.set_yticklabels(fontsize=14)
    return g


def format_stackbar(g, apv_details, xtitle):
    g.set_xlabel(xtitle, fontsize=12, fontweight='bold', labelpad=12)
    xticks = apv_details
    xlabels = []
    for x in xticks:
        if isinstance(x, str):
            xlabels.append(x)
        else:
            xlabels.append('{:,.0f}'.format(x))
    g.set_xticklabels(xlabels, fontsize=14)
    g.set_ylabel('Cost / kW-th', fontsize=16, fontweight='bold', labelpad=12)
    yticks = g.get_yticks()
    g.tick_params(axis='y', which='both', color="#DDDDDD", width=0.5)
    ylabels = ['$' + '{:,.0f}'.format(y) for y in yticks]
    g.set_yticklabels(ylabels, fontsize=14)
    handles, labels = g.get_legend_handles_labels()
    g.legend(handles[::-1], labels[::-1], fontsize=14, frameon=True, edgecolor="white", framealpha=1,
             bbox_to_anchor=(1.02, 1), loc='upper left',)
    g.figure.set_size_inches(8, 6)
    g.set_frame_on(False)
    g.set_axisbelow(True)
    g.grid(axis='y', which='both', color="#DDDDDD", linewidth=0.5)
    return g
