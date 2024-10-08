import ROOT
import argparse
from CombineHarvester.CombineTools.plotting import *
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(ROOT.kTRUE)

parser = argparse.ArgumentParser()
parser.add_argument(
    'input', nargs='+', help="""Input json files""")
parser.add_argument(
    '--output', '-o', default='limit', help="""Name of the output
    plot without file extension""")
parser.add_argument(
    '--show', default='exp,obs')
parser.add_argument(
    '--xtitle', default='m_{#phi} (GeV)', help="""Title for the x-axis""")
parser.add_argument(
    '--ytitle', default='95% CL limit on #mu', help="""Title for the y-axis""")
    #'--ytitle', default='95% CL limit on eff*acc', help="""Title for the y-axis""")
parser.add_argument(
    '--cms-sub', default='Internal', help="""Text below the CMS logo""")
parser.add_argument(
    '--scenario-label', default='', help="""Scenario name to be drawn in top
    left of plot""")
parser.add_argument(
    '--title-right', default='', help="""Right header text above the frame""")
parser.add_argument(
    '--title-left', default='', help="""Left header text above the frame""")
parser.add_argument(
    '--logy', action='store_true', help="""Draw y-axis in log scale""")
parser.add_argument(
    '--logx', action='store_true', help="""Draw x-axis in log scale""")
args = parser.parse_args()

print('Creating Limit for input ', args.input)

# Scaling factor
scale_factor = 1  # Example: 0.657*9.85e-2*0.876

# Style and pads
ModTDRStyle()
canv = ROOT.TCanvas('limit', 'limit')
pads = OnePad()

# Get limit TGraphs as a dictionary
graphs = StandardLimitsFromJSONFile(args.input[0], args.show.split(','))

# Apply the scaling factor to the graphs
for key in ['exp0', 'exp1', 'exp2']:
    if key in graphs:
        graph = graphs[key]
        for i in range(graph.GetN()):
            x, y = ROOT.Double(0), ROOT.Double(0)
            graph.GetPoint(i, x, y)
            y *= scale_factor
            graph.SetPoint(i, x, y)
            
            # Only scale errors if it's a TGraphAsymmErrors
            if isinstance(graph, ROOT.TGraphAsymmErrors):
                yerr_low = graph.GetErrorYlow(i)
                yerr_high = graph.GetErrorYhigh(i)
                graph.SetPointEYlow(i, yerr_low * scale_factor)
                graph.SetPointEYhigh(i, yerr_high * scale_factor)

# Create an empty TH1 from the first TGraph to serve as the pad axis and frame
axis = CreateAxisHist(graphs[list(graphs.keys())[0]])
axis.GetXaxis().SetTitle(args.xtitle)
axis.GetYaxis().SetTitle(args.ytitle)
pads[0].cd()
axis.Draw('axis')

# Create a legend in the top left
legend = PositionedLegend(0.3, 0.2, 3, 0.015)

# Set the standard green and yellow colors and draw
StyleLimitBand(graphs, 
    {
        'obs' : { 'LineWidth' : 2},
        'exp0' : { 'LineWidth' : 2, 'LineColor' : ROOT.kBlack, 'LineStyle': 2},
        'exp1' : { 'FillColor' : ROOT.kGreen},
        'exp2' : { 'FillColor' : ROOT.kYellow}
    }
)
DrawLimitBand(pads[0], graphs, legend=legend)
legend.Draw()

# Re-draw the frame and tick marks
pads[0].RedrawAxis()
pads[0].GetFrame().Draw()

# Adjust the y-axis range such that the maximum graph value sits 25% below the top of the frame. Fix the minimum to zero.
FixBothRanges(pads[0], 0., 0., GetPadYMax(pads[0]), 0.25)
if args.logy:
    FixBothRanges(pads[0], 0.5, 0., 250., 0.)

# Standard CMS logo
DrawCMSLogo(pads[0], 'CMS', args.cms_sub, 11, 0.045, 0.035, 1.2, '', 0.8)
pads[0].SetLogy(args.logy)
pads[0].SetLogx(args.logx)

canv.Print('%s_fullcomb.pdf' % args.output)
canv.Print('%s_fullcomb.root' % args.output)