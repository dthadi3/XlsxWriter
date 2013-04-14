###############################################################################
#
# Chart - A class for writing the Excel XLSX Worksheet file.
#
# Copyright 2013, John McNamara, jmcnamara@cpan.org
#
from warnings import warn

from . import xmlwriter


class Chart(xmlwriter.XMLwriter):
    """
    A class for writing the Excel XLSX Chart file.


    """

    ###########################################################################
    #
    # Public API.
    #
    ###########################################################################

    def __init__(self):
        """
        Constructor.

        """

        super(Chart, self).__init__()

        self.sheet_type = 0x0200
        self.orientation = 0x0
        self.series = []
        self.embedded = 0
        self.id = ''
        self.series_index = 0
        self.style_id = 2
        self.axis_ids = []
        self.axis2_ids = []
        self.cat_has_num_fmt = 0
        self.requires_category = 0
        self.legend_position = 'right'
        self.cat_axis_position = 'b'
        self.val_axis_position = 'l'
        self.formula_ids = {}
        self.formula_data = []
        self.horiz_cat_axis = 0
        self.horiz_val_axis = 1
        self.protection = 0
        self.chartarea = {}
        self.plotarea = {}
        self.x_axis = {}
        self.y_axis = {}
        self.y2_axis = {}
        self.x2_axis = {}
        self.chart_name = ''
        self.show_blanks = 'gap'
        self.show_hidden_data = 0
        self.show_crosses = 1
        self.width = 480
        self.height = 288
        self.x_scale = 1
        self.y_scale = 1
        self.x_offset = 0
        self.y_offset = 0
        self.table = None

    def add_series(self, options):
        # Add a series and it's properties to a chart.

        # Check that the required input has been specified.
        if not 'values' in options:
            warn("Must specify 'values' in add_series()")
            return

        if self.requires_category and not 'categories' in options:
            warn("Must specify 'categories' in add_series() "
                 "for this chart type")

        # Convert list into a formula string.
        values = self._list_to_formula(options.get('values'))
        categories = self._list_to_formula(options.get('categories'))

        # Switch name and name_formula parameters if required.
        name, name_formula = self._process_names(options.get('name'),
                                                 options.get('name_formula'))

        # Get an id for the data equivalent to the range formula.
        cat_id = self._get_data_id(categories, options.get('categories_data'))
        val_id = self._get_data_id(values, options.get('values_data'))
        name_id = self._get_data_id(name_formula, options.get('name_data'))

        # Set the line properties for the series.
        line = self._get_line_properties(options.get('line'))

        # Allow 'border' as a synonym for 'line' in bar/column style charts.
        if options.get('border'):
            line = self._get_line_properties(options['border'])

        # Set the fill properties for the series.
        fill = self._get_fill_properties(options.get('fill'))

        # Set the marker properties for the series.
        marker = self._get_marker_properties(options.get('marker'))

        # Set the trendline properties for the series.
        trendline = self._get_trendline_properties(options.get('trendline'))

        # Set the error bars properties for the series.
        y_error_bars = self._get_error_bars_props(options.get('y_error_bars'))
        x_error_bars = self._get_error_bars_props(options.get('x_error_bars'))

        error_bars = {'x_error_bars': x_error_bars,
                      'y_error_bars': y_error_bars},

        # Set the point properties for the series.
        points = self._get_points_properties(options.get('points'))

        # Set the labels properties for the series.
        labels = self._get_labels_properties(options.get('data_labels'))

        # Set the "invert if negative" fill property.
        invert_if_neg = options.get('invert_if_negative', False)

        # Set the gap for Bar/Column charts.
        if options.get('gap'):
            self.series_gap = options['gap']

        # Set the overlap for Bar/Column charts.
        if options.get('overlap'):
            self.series_overlap = options['overlap']

        # Set the secondary axis properties.
        x2_axis = options.get('x2_axis')
        y2_axis = options.get('y2_axis')

        # Add the user supplied data to the internal structures.
        series = {
            'values': values,
            'categories': categories,
            'name': name,
            'name_formula': name_formula,
            'name_id': name_id,
            'val_data_id': val_id,
            'cat_data_id': cat_id,
            'line': line,
            'fill': fill,
            'marker': marker,
            'trendline': trendline,
            'labels': labels,
            'invert_if_neg': invert_if_neg,
            'x2_axis': x2_axis,
            'y2_axis': y2_axis,
            'points': points,
            'error_bars': error_bars,
        }

        self.series.append(series)

    def set_x_axis(self, options):
        # Set the properties of the X-axis.
        axis = self._convert_axis_args(self.x_axis, options)

        self.x_axis = axis

    def set_y_axis(self, options):
        # Set the properties of the Y-axis.
        axis = self._convert_axis_args(self.y_axis, options)

        self.y_axis = axis

    def set_x2_axis(self, options):
        # Set the properties of the secondary X-axis.
        axis = self._convert_axis_args(self.x2_axis, options)

        self.x2_axis = axis

    def set_y2_axis(self, options):
        # Set the properties of the secondary Y-axis.
        axis = self._convert_axis_args(self.y2_axis, options)

        self.y2_axis = axis

    def set_title(self, options):
        # Set the properties of the chart title.

        name, name_formula = self._process_names(options.get('name'),
                                                 options.get('name_formula'))

        data_id = self._get_data_id(name_formula, options.get('data'))

        self.title_name = name
        self.title_formula = name_formula
        self.title_data_id = data_id

        # Set the font properties if present.
        self.title_font = self._convert_font_args(options.get('name_font'))

    def set_legend(self, options):
        # Set the properties of the chart legend.

        self.legend_position = options.get('position', 'right')
        self.legend_delete_series = options.get('delete_series')

    def set_plotarea(self, options):
        # Set the properties of the chart plotarea.
        # Convert the user defined properties to internal properties.
        self.plotarea = self._get_area_properties(options)

    def set_chartarea(self, options):
        # Set the properties of the chart chartarea.
        # Convert the user defined properties to internal properties.
        self.chartarea = self._get_area_properties(options)

    def set_style(self, style_id):
        # Set one of the 42 built-in Excel chart styles. The default is 2.
        if style_id is None:
            style_id = 2

        if style_id < 0 or style_id > 42:
            style_id = 2

        self.style_id = style_id

    def show_blanks_as(self, option):
        # Set the option for displaying blank data in a chart.
        if not option:
            return

        valid_options = {
            'gap': 1,
            'zero': 1,
            'span': 1,
        }

        if not 'option' in valid_options:
            warn("Unknown show_blanks_as() option '%s'" % option)
            return

        self.show_blanks = option

    def show_hidden_data(self):
        # Display data in hidden rows or columns.
        self.show_hidden_data = 1

    def set_size(self, options):
        # Set dimensions or scale for the chart.
        self.width = options.get('width')
        self.height = options.get('height')
        self.x_scale = options.get('x_scale')
        self.y_scale = options.get('y_scale')
        self.x_offset = options.get('x_offset')
        self.x_offset = options.get('y_offset')

    def set_table(self, args):
        # Set properties for an axis data table.
        table = {
            'horizontal': 1,
            'vertical': 1,
            'outline': 1,
            'show_keys': 0,
        }

        if 'horizontal' in args:
            table['horizontal'] = args.get('horizontal')

        if 'vertical' in args:
            table['vertical'] = args.get('vertical')

        if 'outline' in args:
            table['outline'] = args.get('outline')

        if 'show_keys' in args:
            table['show_keys'] = args.get('show_keys')

        self.table = table

    def set_up_down_bars(self, options):
        # Set properties for the chart up-down bars.
        if options is None:
            return

        # Defaults.
        up_line = None
        up_fill = None
        down_line = None
        down_fill = None

        # Set properties for 'up' bar.
        if options.get('up'):
            # Map border to line.
            if 'border' in options['up']:
                options['up']['line'] = options['up']['border']

            if 'line' in options['up']:
                up_line = self._get_line_properties(options['up']['line'])

            if 'fill' in options['up']:
                up_line = self._get_line_properties(options['up']['fill'])

        # Set properties for 'down' bar.
        if options.get('down'):
            # Map border to line.
            if 'border' in options['down']:
                options['down']['line'] = options['down']['border']

            if 'line' in options['down']:
                down_line = self._get_line_properties(options['down']['line'])

            if 'fill' in options['down']:
                down_line = self._get_line_properties(options['down']['fill'])

        self.up_down_bars = {'up': {'line': up_line,
                                    'fill': up_fill,
                                    },
                             'down': {'line': down_line,
                                      'fill': down_fill,
                                      },
                             }

    def set_drop_lines(self, options):
        # Set properties for the chart drop lines.
        line = self._get_line_properties(options.get('line'))

        self.drop_lines = {'line': line}

    def set_high_low_lines(self, options):
        # Set properties for the chart high-low lines.
        line = self._get_line_properties(options.get('line'))

        self.hi_low_lines = {'line': line}

    ###########################################################################
    #
    # Private API.
    #
    ###########################################################################

    def _assemble_xml_file(self):
        # Assemble and write the XML file.

        # Write the XML declaration.
        self._xml_declaration()

        # Write the c:chartSpace element.
        self._write_chart_space()

        # Write the c:lang element.
        self._write_lang()

        # Write the c:style element.
        self._write_style()

        # Write the c:protection element.
        self._write_protection()

        # Write the c:chart element.
        self._write_chart()

        # Write the c:spPr element for the chartarea formatting.
        self._write_sp_pr(self.chartarea)

        # Write the c:printSettings element.
        if self.embedded:
            self._write_print_settings()

        # Close the worksheet tag.
        self._xml_end_tag('c:chartSpace')
        # Close the file.
        self._xml_close()


    ###########################################################################
    #
    # XML methods.
    #
    ###########################################################################

    def _write_chart_space(self):
        # XML writing methods.
        # Write the <c:chartSpace> element.
        schema = 'http://schemas.openxmlformats.org/'
        xmlns_c = schema + 'drawingml/2006/chart'
        xmlns_a = schema + 'drawingml/2006/main'
        xmlns_r = schema + 'officeDocument/2006/relationships'

        attributes = [
            ('xmlns:c', xmlns_c),
            ('xmlns:a', xmlns_a),
            ('xmlns:r', xmlns_r),
        ]

        self._xml_start_tag('c:chartSpace', attributes)

    def _write_lang(self):
        # Write the <c:lang> element.
        val = 'en-US'

        attributes = [('val', val)]

        self._xml_empty_tag('c:lang', attributes)

    def _write_style(self):
        # Write the <c:style> element.
        style_id = self.style_id

        # Don't write an element for the default style, 2.
        if style_id == 2:
            return

        attributes = [('val', style_id)]

        self._xml_empty_tag('c:style', attributes)

    def _write_chart(self):
        # Write the <c:chart> element.
        self._xml_start_tag('c:chart')

        # Write the chart title elements.

        if self.title_formula:
            self._write_title_formula(self.title_formula, self.title_data_id,
                                      None, self.title_font)
        elif self.title_name:
            self._write_title_rich(self.title_name, None, self.title_font)

        # Write the c:plotArea element.
        self._write_plot_area()

        # Write the c:legend element.
        self._write_legend()

        # Write the c:plotVisOnly element.
        self._write_plot_vis_only()

        # Write the c:dispBlanksAs element.
        self._write_disp_blanks_as()

        self._xml_end_tag('c:chart')

    def _write_disp_blanks_as(self):
        # Write the <c:dispBlanksAs> element.
        val = self.show_blanks

        # Ignore the default value.
        if val == 'gap':
            return

        attributes = [('val', val)]

        self._xml_empty_tag('c:dispBlanksAs', attributes)

    def _write_plot_area(self):
        # Write the <c:plotArea> element.
        self._xml_start_tag('c:plotArea')

        # Write the c:layout element.
        self._write_layout()

        # Write  subclass chart type elements for primary and secondary axes.
        self._write_chart_type({'primary_axes': True})
        self._write_chart_type({'primary_axes': False})

        # Write c:catAx and c:valAx elements for series using primary axes.
        self._write_cat_axis({'x_axis': self.x_axis,
                              'y_axis': self.y_axis,
                              'axis_ids': self.axis_ids
                              })

        self._write_val_axis({'x_axis': self.x_axis,
                              'y_axis': self.y_axis,
                              'axis_ids': self.axis_ids
                              })

        # Write c:valAx and c:catAx elements for series using secondary axes.
        self._write_val_axis({'x_axis': self.x2_axis,
                              'y_axis': self.y2_axis,
                              'axis_ids': self.axis2_ids
                              })

        self._write_cat_axis({'x_axis': self.x2_axis,
                              'y_axis': self.y2_axis,
                              'axis_ids': self.axis2_ids
                              })

        # Write the c:dTable element.
        self._write_d_table()

        # Write the c:spPr element for the plotarea formatting.
        self._write_sp_pr(self.plotarea)

        self._xml_end_tag('c:plotArea')

    def _write_layout(self):
        # Write the <c:layout> element.
        self._xml_empty_tag('c:layout')

    def _write_chart_type(self):
        # Write the chart type element. This method should be overridden by the
        # subclasses.
        pass

    def _write_grouping(self, val):
        # Write the <c:grouping> element.
        attributes = [('val', val)]

        self._xml_empty_tag('c:grouping', attributes)

    def _write_series(self, series):
        # Write the series elements.
        self._write_ser(series)

    def _write_ser(self, series):
        # Write the <c:ser> element.
        index = self.series_index
        self.series_index += 1

        self._xml_start_tag('c:ser')

        # Write the c:idx element.
        self._write_idx(index)

        # Write the c:order element.
        self._write_order(index)

        # Write the series name.
        self._write_series_name(series)

        # Write the c:spPr element.
        self._write_sp_pr(series)

        # Write the c:marker element.
        self._write_marker(series.marker)

        # Write the c:invertIfNegative element.
        self._write_c_invert_if_negative(series.invert_if_neg)

        # Write the c:dPt element.
        self._write_d_pt(series.points)

        # Write the c:dLbls element.
        self._write_d_lbls(series.labels)

        # Write the c:trendline element.
        self._write_trendline(series.trendline)

        # Write the c:errBars element.
        self._write_error_bars(series.error_bars)

        # Write the c:cat element.
        self._write_cat(series)

        # Write the c:val element.
        self._write_val(series)

        self._xml_end_tag('c:ser')

    def _write_idx(self, val):
        # Write the <c:idx> element.

        attributes = [('val', val)]

        self._xml_empty_tag('c:idx', attributes)

    def _write_order(self, val):
        # Write the <c:order> element.

        attributes = [('val', val)]

        self._xml_empty_tag('c:order', attributes)

    def _write_series_name(self, series):
        # Write the series name.
        if series.name_formula:
            self._write_tx_formula(series.name_formula, series.name_id)
        elif series.name:
            self._write_tx_value(series.name)

    def _write_cat(self, series):
        # Write the <c:cat> element.
        formula = series.categories
        data_id = series.cat_data_id
        data = None

        if data_id:
            data = self.formula_data[data_id]

        # Ignore <c:cat> elements for charts without category values.
        if not formula:
            return

        self._xml_start_tag('c:cat')

        # Check the type of cached data.
        cat_type = self._get_data_type(data)

        if cat_type == 'str':
            self.cat_has_num_fmt = 0
            # Write the c:numRef element.
            self._write_str_ref(formula, data, cat_type)
        else:
            self.cat_has_num_fmt = 1
            # Write the c:numRef element.
            self._write_num_ref(formula, data, cat_type)

        self._xml_end_tag('c:cat')

    def _write_val(self, series):
        # Write the <c:val> element.
        formula = series.values
        data_id = series.val_data_id
        data = self.formula_data[data_id]

        self._xml_start_tag('c:val')

        # Unlike Cat axes data should only be numeric.
        # Write the c:numRef element.
        self._write_num_ref(formula, data, 'num')

        self._xml_end_tag('c:val')

    def _write_num_ref(self, formula, data, ref_type):
        # Write the <c:numRef> element.
        self._xml_start_tag('c:numRef')

        # Write the c:f element.
        self._write_series_formula(formula)

        if ref_type == 'num':
            # Write the c:numCache element.
            self._write_num_cache(data)
        elif ref_type == 'str':
            # Write the c:strCache element.
            self._write_str_cache(data)

        self._xml_end_tag('c:numRef')

    def _write_str_ref(self, formula, data, ref_type):
        # Write the <c:strRef> element.

        self._xml_start_tag('c:strRef')

        # Write the c:f element.
        self._write_series_formula(formula)

        if ref_type == 'num':
            # Write the c:numCache element.
            self._write_num_cache(data)
        elif ref_type == 'str':
            # Write the c:strCache element.
            self._write_str_cache(data)

        self._xml_end_tag('c:strRef')

    def _write_series_formula(self, formula):
        # Write the <c:f> element.

        # Strip the leading '=' from the formula.
        if formula.startswith('='):
            formula = formula.lstrip('=')

        self._xml_data_element('c:f', formula)

    def _write_axis_ids(self, args):
        # Write the <c:axId> elements for the primary or secondary axes.

        # Generate the axis ids.
        self._add_axis_ids(args)

        if args['primary_axes']:

            # Write the axis ids for the primary axes.
            self._write_axis_id(self.axis_ids[0])
            self._write_axis_id(self.axis_ids[1])
        else:
            # Write the axis ids for the secondary axes.
            self._write_axis_id(self.axis2_ids[0])
            self._write_axis_id(self.axis2_ids[1])

    def _write_axis_id(self, val):
        # Write the <c:axId> element.

        attributes = [('val', val)]

        self._xml_empty_tag('c:axId', attributes)

    def _write_cat_axis(self, args):
        # Write the <c:catAx> element. Usually the X axis.
        x_axis = args['x_axis']
        y_axis = args['y_axis']
        axis_ids = args['axis_ids']

        # if there are no axis_ids then we don't need to write this element
        if not axis_ids or not len(axis_ids):
            return

        position = self.cat_axis_position
        horiz = self.horiz_cat_axis

        # Overwrite the default axis position with a user supplied value.
        position = x_axis.position or position

        self._xml_start_tag('c:catAx')

        self._write_axis_id(axis_ids[0])

        # Write the c:scaling element.
        self._write_scaling(x_axis.reverse)

        if not x_axis.visible:
            self._write_delete(1)

        # Write the c:axPos element.
        self._write_axis_pos(position, y_axis.reverse)

        # Write the c:majorGridlines element.
        self._write_major_gridlines(x_axis.major_gridlines)

        # Write the c:minorGridlines element.
        self._write_minor_gridlines(x_axis.minor_gridlines)

        # Write the axis title elements.
        if x_axis.formula:
            self._write_title_formula(x_axis.formula, x_axis.data_id, horiz,
                                      x_axis.name_font)
        elif x_axis.name:
            self._write_title_rich(x_axis.name, horiz, x_axis.name_font)

        # Write the c:numFmt element.
        self._write_cat_number_format(x_axis)

        # Write the c:majorTickMark element.
        self._write_major_tick_mark(x_axis.major_tick_mark)

        # Write the c:tickLblPos element.
        self._write_tick_label_pos(x_axis.label_position)

        # Write the axis font elements.
        self._write_axis_font(x_axis.num_font)

        # Write the c:crossAx element.
        self._write_cross_axis(axis_ids[1])

        if self.show_crosses or x_axis.visible:

            # Note, the category crossing comes from the value axis.
            if y_axis.crossing is None or y_axis.crossing == 'max':

                # Write the c:crosses element.
                self._write_crosses(y_axis.crossing)
            else:

                # Write the c:crossesAt element.
                self._write_c_crosses_at(y_axis.crossing)

        # Write the c:auto element.
        self._write_auto(1)

        # Write the c:labelAlign element.
        self._write_label_align('ctr')

        # Write the c:labelOffset element.
        self._write_label_offset(100)

        self._xml_end_tag('c:catAx')

    def _write_val_axis(self, args):
        # Write the <c:valAx> element. Usually the Y axis.
        x_axis = args['x_axis']
        y_axis = args['y_axis']
        axis_ids = args['axis_ids']
        position = args['position'] or self.val_axis_position
        horiz = self.horiz_val_axis

        if not axis_ids and len(axis_ids):
            return

        # Overwrite the default axis position with a user supplied value.
        position = y_axis.position or position

        self._xml_start_tag('c:valAx')

        self._write_axis_id(axis_ids[1])

        # Write the c:scaling element.
        self._write_scaling(y_axis.reverse,
                            y_axis.min,
                            y_axis.max,
                            y_axis.log_base)

        if not y_axis.visible:
            self._write_delete(1)

        # Write the c:axPos element.
        self._write_axis_pos(position, x_axis.reverse)

        # Write the c:majorGridlines element.
        self._write_major_gridlines(y_axis.major_gridlines)

        # Write the c:minorGridlines element.
        self._write_minor_gridlines(y_axis.minor_gridlines)

        # Write the axis title elements.
        if y_axis.formula:
            self._write_title_formula(y_axis.formula, y_axis.data_id, horiz,
                                      y_axis.name_font)
        elif y_axis.name:
            self._write_title_rich(y_axis.name, horiz, y_axis.name_font)

        # Write the c:numberFormat element.
        self._write_number_format(y_axis)

        # Write the c:majorTickMark element.
        self._write_major_tick_mark(y_axis.major_tick_mark)

        # Write the c:tickLblPos element.
        self._write_tick_label_pos(y_axis.label_position)

        # Write the axis font elements.
        self._write_axis_font(y_axis.num_font)

        # Write the c:crossAx element.
        self._write_cross_axis(axis_ids[0])

        # Note, the category crossing comes from the value axis.
        if x_axis.crossing is None or x_axis.crossing == 'max':

            # Write the c:crosses element.
            self._write_crosses(x_axis.crossing)
        else:

            # Write the c:crossesAt element.
            self._write_c_crosses_at(x_axis.crossing)

        # Write the c:crossBetween element.
        self._write_cross_between()

        # Write the c:majorUnit element.
        self._write_c_major_unit(y_axis.major_unit)

        # Write the c:minorUnit element.
        self._write_c_minor_unit(y_axis.minor_unit)

        self._xml_end_tag('c:valAx')

    def _write_cat_val_axis(self, args):
        # Write the <c:valAx> element. This is for the second valAx
        # in scatter plots. Usually the X axis.
        x_axis = args['x_axis']
        y_axis = args['y_axis']
        axis_ids = args['axis_ids']
        position = args['position'] or self.val_axis_position
        horiz = self.horiz_val_axis

        if not axis_ids and len(axis_ids):
            return

        # Overwrite the default axis position with a user supplied value.
        position = x_axis.position or position

        self._xml_start_tag('c:valAx')

        self._write_axis_id(axis_ids[0])

        # Write the c:scaling element.
        self._write_scaling(x_axis.reverse,
                            x_axis.min,
                            x_axis.max,
                            x_axis.log_base)

        if not x_axis.visible:
            self._write_delete(1)

        # Write the c:axPos element.
        self._write_axis_pos(position, y_axis.reverse)

        # Write the c:majorGridlines element.
        self._write_major_gridlines(x_axis.major_gridlines)

        # Write the c:minorGridlines element.
        self._write_minor_gridlines(x_axis.minor_gridlines)

        # Write the axis title elements.
        if x_axis.formula:
            self._write_title_formula(x_axis.formula, y_axis.data_id, horiz,
                                      x_axis.name_font)
        elif x_axis.name:
            self._write_title_rich(x_axis.name_font, horiz, x_axis.name_font)

        # Write the c:numberFormat element.
        self._write_number_format(x_axis)

        # Write the c:majorTickMark element.
        self._write_major_tick_mark(x_axis.major_tick_mark)

        # Write the c:tickLblPos element.
        self._write_tick_label_pos(x_axis.label_position)

        # Write the axis font elements.
        self._write_axis_font(x_axis.num_font)

        # Write the c:crossAx element.
        self._write_cross_axis(axis_ids[1])

        # Note, the category crossing comes from the value axis.
        if y_axis.crossing is None or y_axis.crossing == 'max':

            # Write the c:crosses element.
            self._write_crosses(y_axis.crossing)
        else:

            # Write the c:crossesAt element.
            self._write_c_crosses_at(y_axis.crossing)

        # Write the c:crossBetween element.
        self._write_cross_between()

        # Write the c:majorUnit element.
        self._write_c_major_unit(x_axis.major_unit)

        # Write the c:minorUnit element.
        self._write_c_minor_unit(x_axis.minor_unit)

        self._xml_end_tag('c:valAx')

    def _write_date_axis(self, args):
        # Write the <c:dateAx> element. Usually the X axis.
        x_axis = args['x_axis']
        y_axis = args['y_axis']
        axis_ids = args['axis_ids']

        if not axis_ids and len(axis_ids):
            return

        position = self.cat_axis_position

        # Overwrite the default axis position with a user supplied value.
        position = x_axis.position or position

        self._xml_start_tag('c:dateAx')

        self._write_axis_id(axis_ids[0])

        # Write the c:scaling element.
        self._write_scaling(x_axis.reverse,
                            x_axis.min,
                            x_axis.max,
                            x_axis.log_base)

        if not x_axis.visible:
            self._write_delete(1)

        # Write the c:axPos element.
        self._write_axis_pos(position, y_axis.reverse)

        # Write the c:majorGridlines element.
        self._write_major_gridlines(x_axis.major_gridlines)

        # Write the c:minorGridlines element.
        self._write_minor_gridlines(x_axis.minor_gridlines)

        # Write the axis title elements.
        if x_axis.formula:
            self._write_title_formula(x_axis.formula, x_axis.data_id, None,
                                      x_axis.name_font)
        elif x_axis.name:
            self._write_title_rich(x_axis.name_font, None, x_axis.name_font)

        # Write the c:numFmt element.
        self._write_number_format(x_axis)

        # Write the c:majorTickMark element.
        self._write_major_tick_mark(x_axis.major_tick_mark)

        # Write the c:tickLblPos element.
        self._write_tick_label_pos(x_axis.label_position)

        # Write the axis font elements.
        self._write_axis_font(x_axis.num_font)

        # Write the c:crossAx element.
        self._write_cross_axis(axis_ids[1])

        if self.show_crosses or x_axis.visible:

            # Note, the category crossing comes from the value axis.
            if y_axis.crossing is None or y_axis.crossing == 'max':

                # Write the c:crosses element.
                self._write_crosses(y_axis.crossing)
            else:

                # Write the c:crossesAt element.
                self._write_c_crosses_at(y_axis.crossing)

        # Write the c:auto element.
        self._write_auto(1)

        # Write the c:labelOffset element.
        self._write_label_offset(100)

        # Write the c:majorUnit element.
        self._write_c_major_unit(x_axis.major_unit)

        # Write the c:majorTimeUnit element.
        if x_axis.major_unit:
            self._write_c_major_time_unit(x_axis.major_unit_type)

        # Write the c:minorUnit element.
        self._write_c_minor_unit(x_axis.minor_unit)

        # Write the c:minorTimeUnit element.
        if x_axis.minor_unit:
            self._write_c_minor_time_unit(x_axis.minor_unit_type)

        self._xml_end_tag('c:dateAx')

    def _write_scaling(self, reverse, min_val, max_val, log_base):
        # Write the <c:scaling> element.

        self._xml_start_tag('c:scaling')

        # Write the c:logBase element.
        self._write_c_log_base(log_base)

        # Write the c:orientation element.
        self._write_orientation(reverse)

        # Write the c:max element.
        self._write_c_max(max_val)

        # Write the c:min element.
        self._write_c_min(min_val)

        self._xml_end_tag('c:scaling')

    def _write_c_log_base(self, val):
        # Write the <c:logBase> element.

        if not val:
            return

        attributes = [('val', val)]

        self._xml_empty_tag('c:logBase', attributes)

    def _write_orientation(self, reverse):
        # Write the <c:orientation> element.
        val = 'minMax'

        if reverse:
            val = 'maxMin'

        attributes = [('val', val)]

        self._xml_empty_tag('c:orientation', attributes)

    def _write_c_max(self, max_val):
        # Write the <c:max_val> element.

        if max_val is None:
            return

        attributes = [('val', max_val)]

        self._xml_empty_tag('c:max', attributes)

    def _write_c_min(self, min_val):
        # Write the <c:min_val> element.

        if min_val is None:
            return

        attributes = [('val', min_val)]

        self._xml_empty_tag('c:min', attributes)

    def _write_axis_pos(self, val, reverse):
        # Write the <c:axPos> element.

        if reverse:
            if val == 'l':
                val = 'r'
            if val == 'b':
                val = 't'

        attributes = [('val', val)]

        self._xml_empty_tag('c:axPos', attributes)

    def _write_number_format(self, axis):
        # Write the <c:numberFormat> element. Note: It is assumed that if
        # a user defined number format is supplied (i.e., non-default) then
        # the sourceLinked attribute is 0.
        # The user can override this if required.
        format_code = axis.num_format
        source_linked = 1

        # Check if a user defined number format has been set.
        if format_code != axis.defaults['num_format']:
            source_linked = 0

        # User override of sourceLinked.
        if axis.num_format_linked:
            source_linked = 1

        attributes = [
            ('formatCode', format_code),
            ('sourceLinked', source_linked),
        ]

        self._xml_empty_tag('c:numFmt', attributes)

    def _write_cat_number_format(self, axis):
        # Write the <c:numFmt> element. Special case handler for category
        # axes which don't always have a number format.
        format_code = axis.num_format
        source_linked = 1
        default_format = 1

        # Check if a user defined number format has been set.
        if format_code != axis.defaults['num_format']:
            source_linked = 0
            default_format = 0

        # User override of linkedSource.
        if axis.num_format_linked:
            source_linked = 1

        # Skip if cat doesn't have a num format (unless it is non-default).
        if not self.cat_has_num_fmt and default_format:
            return

        attributes = [
            ('formatCode', format_code),
            ('sourceLinked', source_linked),
        ]

        self._xml_empty_tag('c:numFmt', attributes)

    def _write_major_tick_mark(self, val):
        # Write the <c:majorTickMark> element.

        if not val:
            return

        attributes = [('val', val)]

        self._xml_empty_tag('c:majorTickMark', attributes)

    def _write_tick_label_pos(self, val=None):
        # Write the <c:tickLblPos> element.
        if val is None or val == 'continue_to':
            val = 'continueTo'

        attributes = [('val', val)]

        self._xml_empty_tag('c:tickLblPos', attributes)

    def _write_cross_axis(self, val):
        # Write the <c:crossAx> element.

        attributes = [('val', val)]

        self._xml_empty_tag('c:crossAx', attributes)

    def _write_crosses(self, val=None):
        # Write the <c:crosses> element.
        if val is None:
            val = 'autoZero'

        attributes = [('val', val)]

        self._xml_empty_tag('c:crosses', attributes)

    def _write_c_crosses_at(self, val):
        # Write the <c:crossesAt> element.

        attributes = [('val', val)]

        self._xml_empty_tag('c:crossesAt', attributes)

    def _write_auto(self, val):
        # Write the <c:auto> element.

        attributes = [('val', val)]

        self._xml_empty_tag('c:auto', attributes)

    def _write_label_align(self):
        # Write the <c:labelAlign> element.
        val = 'ctr'

        attributes = [('val', val)]

        self._xml_empty_tag('c:lblAlgn', attributes)

    def _write_label_offset(self, val):
        # Write the <c:labelOffset> element.

        attributes = [('val', val)]

        self._xml_empty_tag('c:lblOffset', attributes)

    def _write_major_gridlines(self, gridlines):
        # Write the <c:majorGridlines> element.

        if not gridlines:
            return
        if not gridlines.visible:
            return

        if gridlines['line']['defined']:
            self._xml_start_tag('c:majorGridlines')

            # Write the c:spPr element.
            self._write_sp_pr(gridlines)

            self._xml_end_tag('c:majorGridlines')
        else:
            self._xml_empty_tag('c:majorGridlines')

    def _write_minor_gridlines(self, gridlines):
        # Write the <c:minorGridlines> element.

        if not gridlines:
            return
        if not gridlines.visible:
            return

        if gridlines['line']['defined']:
            self._xml_start_tag('c:minorGridlines')

            # Write the c:spPr element.
            self._write_sp_pr(gridlines)

            self._xml_end_tag('c:minorGridlines')
        else:
            self._xml_empty_tag('c:minorGridlines')

    def _write_cross_between(self):
        # Write the <c:crossBetween> element.
        val = self.cross_between or 'between'

        attributes = [('val', val)]

        self._xml_empty_tag('c:crossBetween', attributes)

    def _write_c_major_unit(self, val):
        # Write the <c:majorUnit> element.

        if not val:
            return

        attributes = [('val', val)]

        self._xml_empty_tag('c:majorUnit', attributes)

    def _write_c_minor_unit(self, val):
        # Write the <c:minorUnit> element.

        if not val:
            return

        attributes = [('val', val)]

        self._xml_empty_tag('c:minorUnit', attributes)

    def _write_c_major_time_unit(self, val=None):
        # Write the <c:majorTimeUnit> element.
        if val is None:
            val = 'days'

        attributes = [('val', val)]

        self._xml_empty_tag('c:majorTimeUnit', attributes)

    def _write_c_minor_time_unit(self, val=None):
        # Write the <c:minorTimeUnit> element.
        if val is None:
            val = 'days'

        attributes = [('val', val)]

        self._xml_empty_tag('c:minorTimeUnit', attributes)

    def _write_legend(self):
        # Write the <c:legend> element.
        position = self.legend_position
        delete_series = ()
        overlay = 0

        # if (self.legend_delete_series is not None
        #    and ref self.legend_delete_series == 'ARRAY'):
        #    delete_series =  self.legend_delete_series

        # if position =~ s/^overlay_//:
        #    overlay = 1

        allowed = {
            'right': 'r',
            'left': 'l',
            'top': 't',
            'bottom': 'b',
        }

        if position == 'none':
            return
        if not 'position' in allowed:
            return

        position = allowed['position']

        self._xml_start_tag('c:legend')

        # Write the c:legendPos element.
        self._write_legend_pos(position)

        # Remove series labels from the legend.
        for index in (delete_series):

            # Write the c:legendEntry element.
            self._write_legend_entry(index)

        # Write the c:layout element.
        self._write_layout()

        # Write the c:overlay element.
        if overlay:
            self._write_overlay()

        self._xml_end_tag('c:legend')

    def _write_legend_pos(self, val):
        # Write the <c:legendPos> element.

        attributes = [('val', val)]

        self._xml_empty_tag('c:legendPos', attributes)

    def _write_legend_entry(self, index):
        # Write the <c:legendEntry> element.

        self._xml_start_tag('c:legendEntry')

        # Write the c:idx element.
        self._write_idx(index)

        # Write the c:delete element.
        self._write_delete(1)

        self._xml_end_tag('c:legendEntry')

    def _write_overlay(self):
        # Write the <c:overlay> element.
        val = 1

        attributes = [('val', val)]

        self._xml_empty_tag('c:overlay', attributes)

    def _write_plot_vis_only(self):
        # Write the <c:plotVisOnly> element.
        val = 1

        # Ignore this element if we are plotting hidden data.
        if self.show_hidden_data:
            return

        attributes = [('val', val)]

        self._xml_empty_tag('c:plotVisOnly', attributes)

    def _write_print_settings(self):
        # Write the <c:printSettings> element.
        self._xml_start_tag('c:printSettings')

        # Write the c:headerFooter element.
        self._write_header_footer()

        # Write the c:pageMargins element.
        self._write_page_margins()

        # Write the c:pageSetup element.
        self._write_page_setup()

        self._xml_end_tag('c:printSettings')

    def _write_header_footer(self):
        # Write the <c:headerFooter> element.
        self._xml_empty_tag('c:headerFooter')

    def _write_page_margins(self):
        # Write the <c:pageMargins> element.
        b = 0.75
        l = 0.7
        r = 0.7
        t = 0.75
        header = 0.3
        footer = 0.3

        attributes = [
            ('b', b),
            ('l', l),
            ('r', r),
            ('t', t),
            ('header', header),
            ('footer', footer),
        ]

        self._xml_empty_tag('c:pageMargins', attributes)

    def _write_page_setup(self):
        # Write the <c:pageSetup> element.
        self._xml_empty_tag('c:pageSetup')

    def _write_title_rich(self, title, horiz, font):
        # Write the <c:title> element for a rich string.

        self._xml_start_tag('c:title')

        # Write the c:tx element.
        self._write_tx_rich(title, horiz, font)

        # Write the c:layout element.
        self._write_layout()

        self._xml_end_tag('c:title')

    def _write_title_formula(self, title, data_id, horiz, font):
        # Write the <c:title> element for a rich string.

        self._xml_start_tag('c:title')

        # Write the c:tx element.
        self._write_tx_formula(title, data_id)

        # Write the c:layout element.
        self._write_layout()

        # Write the c:txPr element.
        self._write_tx_pr(horiz, font)

        self._xml_end_tag('c:title')

    def _write_tx_rich(self, title, horiz, font):
        # Write the <c:tx> element.

        self._xml_start_tag('c:tx')

        # Write the c:rich element.
        self._write_rich(title, horiz, font)

        self._xml_end_tag('c:tx')

    def _write_tx_value(self, title):
        # Write the <c:tx> element with a value such as for series names.

        self._xml_start_tag('c:tx')

        # Write the c:v element.
        self._write_v(title)

        self._xml_end_tag('c:tx')

    def _write_tx_formula(self, title, data_id):
        # Write the <c:tx> element.
        data = None

        if data_id is not None:
            data = self.formula_data[data_id]

        self._xml_start_tag('c:tx')

        # Write the c:strRef element.
        self._write_str_ref(title, data, 'str')

        self._xml_end_tag('c:tx')

    def _write_rich(self, title, horiz, font):
        # Write the <c:rich> element.

        self._xml_start_tag('c:rich')

        # Write the a:bodyPr element.
        self._write_a_body_pr(horiz)

        # Write the a:lstStyle element.
        self._write_a_lst_style()

        # Write the a:p element.
        self._write_a_p_rich(title, font)

        self._xml_end_tag('c:rich')

    def _write_a_body_pr(self, horiz):
        # Write the <a:bodyPr> element.
        rot = -5400000
        vert = 'horz'

        attributes = [
            ('rot', rot),
            ('vert', vert),
        ]

        if not horiz:
            attributes = [()]

        self._xml_empty_tag('a:bodyPr', attributes)

    def _write_a_lst_style(self):
        # Write the <a:lstStyle> element.
        self._xml_empty_tag('a:lstStyle')

    def _write_a_p_rich(self, title, font):
        # Write the <a:p> element for rich string titles.

        self._xml_start_tag('a:p')

        # Write the a:pPr element.
        self._write_a_p_pr_rich(font)

        # Write the a:r element.
        self._write_a_r(title, font)

        self._xml_end_tag('a:p')

    def _write_a_p_formula(self, font):
        # Write the <a:p> element for formula titles.

        self._xml_start_tag('a:p')

        # Write the a:pPr element.
        self._write_a_p_pr_formula(font)

        # Write the a:endParaRPr element.
        self._write_a_end_para_rpr()

        self._xml_end_tag('a:p')

    def _write_a_p_pr_rich(self, font):
        # Write the <a:pPr> element for rich string titles.

        self._xml_start_tag('a:pPr')

        # Write the a:defRPr element.
        self._write_a_def_rpr(font)

        self._xml_end_tag('a:pPr')

    def _write_a_p_pr_formula(self, font):
        # Write the <a:pPr> element for formula titles.

        self._xml_start_tag('a:pPr')

        # Write the a:defRPr element.
        self._write_a_def_rpr(font)

        self._xml_end_tag('a:pPr')

    def _write_a_def_rpr(self, font):
        # Write the <a:defRPr> element.
        has_color = 0

        style_attributes = self._get_font_style_attributes(font)
        latin_attributes = self._get_font_latin_attributes(font)

        if font and font.color:
            has_color = 1

        if latin_attributes or has_color:
            self._xml_start_tag('a:defRPr', style_attributes)

            if has_color:
                self._write_a_solid_fill({'color': font.color})

            if latin_attributes:
                self._write_a_latin(latin_attributes)

            self._xml_end_tag('a:defRPr')
        else:
            self._xml_empty_tag('a:defRPr', style_attributes)

    def _write_a_end_para_rpr(self):
        # Write the <a:endParaRPr> element.
        lang = 'en-US'

        attributes = [('lang', lang)]

        self._xml_empty_tag('a:endParaRPr', attributes)

    def _write_a_r(self, title, font):
        # Write the <a:r> element.

        self._xml_start_tag('a:r')

        # Write the a:rPr element.
        self._write_a_r_pr(font)

        # Write the a:t element.
        self._write_a_t(title)

        self._xml_end_tag('a:r')

    def _write_a_r_pr(self, font):
        # Write the <a:rPr> element.
        # my $self = shift;
        # my $font  = shift;
        # my $lang = 'en-US';
        # my @attributes = ( 'lang' => $lang, );
        # my @font_attrs = $self->_get_font_style_attributes($font);
        # push @attributes, @font_attrs;
        # $self->xml_empty_tag( 'a:rPr', @attributes );
        has_color = 0
        lang = 'en-US'

        style_attributes = self._get_font_style_attributes(font)
        latin_attributes = self._get_font_latin_attributes(font)

        if font and font.color:
            has_color = 1

        # Add the lang type to the attributes.
        style_attributes = [('lang', lang, style_attributes)]

        if latin_attributes or has_color:
            self._xml_start_tag('a:rPr', style_attributes)

            if has_color:
                self._write_a_solid_fill({'color': font.color})

            if latin_attributes:
                self._write_a_latin(latin_attributes)

            self._xml_end_tag('a:rPr')
        else:
            self._xml_empty_tag('a:rPr', style_attributes)

    def _write_a_t(self, title):
        # Write the <a:t> element.

        self._xml_data_element('a:t', title)

    def _write_tx_pr(self, horiz, font):
        # Write the <c:txPr> element.

        self._xml_start_tag('c:txPr')

        # Write the a:bodyPr element.
        self._write_a_body_pr(horiz)

        # Write the a:lstStyle element.
        self._write_a_lst_style()

        # Write the a:p element.
        self._write_a_p_formula(font)

        self._xml_end_tag('c:txPr')

    def _write_marker(self, marker):
        # Write the <c:marker> element.
        if marker is None:
            marker = self.default_marker

        if not marker:
            return
        if marker['automatic']:
            return

        self._xml_start_tag('c:marker')

        # Write the c:symbol element.
        self._write_symbol(marker['type'])

        # Write the c:size element.
        size = marker['size']
        if size:
            self._write_marker_size(size)

        # Write the c:spPr element.
        self._write_sp_pr(marker)

        self._xml_end_tag('c:marker')

    def _write_marker_value(self):
        # Write the <c:marker> element without a sub-element.
        style = self.default_marker

        if not style:
            return

        attributes = [('val', 1)]

        self._xml_empty_tag('c:marker', attributes)

    def _write_marker_size(self, val):
        # Write the <c:size> element.

        attributes = [('val', val)]

        self._xml_empty_tag('c:size', attributes)

    def _write_symbol(self, val):
        # Write the <c:symbol> element.

        attributes = [('val', val)]

        self._xml_empty_tag('c:symbol', attributes)

    def _write_sp_pr(self, series):
        # Write the <c:spPr> element.

        # if (not series.line.and is not None series.fill.) is not None:
        #    return

        self._xml_start_tag('c:spPr')

        # Write the fill elements for solid charts such as pie and bar.
        if (series['fill']['defined']) is not None:

            if series.fill['none']:

                # Write the a:noFill element.
                self._write_a_no_fill()
            else:
                # Write the a:solidFill element.
                self._write_a_solid_fill(series.fill)

        # Write the a:ln element.
        if (series['line']['defined']) is not None:
            self._write_a_ln(series.line)

        self._xml_end_tag('c:spPr')

    def _write_a_ln(self, line):
        # Write the <a:ln> element.
        attributes = []

        # Add the line width as an attribute.
        width = line['width']

        if width:
            # Round width to nearest 0.25, like Excel.
            width = int((width + 0.125) * 4) / 4

            # Convert to internal units.
            width = int(0.5 + (12700 * width))

            attributes = [('w', width)]

        self._xml_start_tag('a:ln', attributes)

        # Write the line fill.
        if line['none']:

            # Write the a:noFill element.
            self._write_a_no_fill()
        elif line['color']:

            # Write the a:solidFill element.
            self._write_a_solid_fill(line)

        # Write the line/dash type.
        line_type = line['dash_type']
        if line_type:
            # Write the a:prstDash element.
            self._write_a_prst_dash(line_type)

        self._xml_end_tag('a:ln')

    def _write_a_no_fill(self):
        # Write the <a:noFill> element.
        self._xml_empty_tag('a:noFill')

    def _write_a_solid_fill(self, line):
        # Write the <a:solidFill> element.

        self._xml_start_tag('a:solidFill')

        if line['color']:

            color = self._get_color(line['color'])

            # Write the a:srgbClr element.
            self._write_a_srgb_clr(color)

        self._xml_end_tag('a:solidFill')

    def _write_a_srgb_clr(self, val):
        # Write the <a:srgbClr> element.

        attributes = [('val', val)]

        self._xml_empty_tag('a:srgbClr', attributes)

    def _write_a_prst_dash(self, val):
        # Write the <a:prstDash> element.

        attributes = [('val', val)]

        self._xml_empty_tag('a:prstDash', attributes)

    def _write_trendline(self, trendline):
        # Write the <c:trendline> element.

        if not trendline:
            return

        self._xml_start_tag('c:trendline')

        # Write the c:name element.
        self._write_name(trendline['name'])

        # Write the c:spPr element.
        self._write_sp_pr(trendline)

        # Write the c:trendlineType element.
        self._write_trendline_type(trendline['type'])

        # Write the c:order element for polynomial trendlines.
        if trendline['type'] == 'poly':
            self._write_trendline_order(trendline['order'])

        # Write the c:period element for moving average trendlines.
        if trendline['type'] == 'movingAvg':
            self._write_period(trendline['period'])

        # Write the c:forward element.
        self._write_forward(trendline['forward'])

        # Write the c:backward element.
        self._write_backward(trendline['backward'])

        self._xml_end_tag('c:trendline')

    def _write_trendline_type(self, val):
        # Write the <c:trendlineType> element.

        attributes = [('val', val)]

        self._xml_empty_tag('c:trendlineType', attributes)

    def _write_name(self, data):
        # Write the <c:name> element.

        if data is None:
            return

        self._xml_data_element('c:name', data)

    def _write_trendline_order(self, val):
        # Write the <c:order> element.
        # val = _[0] is not None ? _[0]: 2

        attributes = [('val', val)]

        self._xml_empty_tag('c:order', attributes)

    def _write_period(self, val):
        # Write the <c:period> element.
        # val = _[0] is not None ? _[0]: 2

        attributes = [('val', val)]

        self._xml_empty_tag('c:period', attributes)

    def _write_forward(self, val):
        # Write the <c:forward> element.

        if not val:
            return

        attributes = [('val', val)]

        self._xml_empty_tag('c:forward', attributes)

    def _write_backward(self, val):
        # Write the <c:backward> element.

        if not val:
            return

        attributes = [('val', val)]

        self._xml_empty_tag('c:backward', attributes)

    def _write_hi_low_lines(self):
        # Write the <c:hiLowLines> element.
        hi_low_lines = self.hi_low_lines

        if not hi_low_lines:
            return

        if hi_low_lines.line['defined']:

            self._xml_start_tag('c:hiLowLines')

            # Write the c:spPr element.
            self._write_sp_pr(hi_low_lines)

            self._xml_end_tag('c:hiLowLines')
        else:
            self._xml_empty_tag('c:hiLowLines')

    def _write_drop_lines(self):
        # Write the <c:dropLines> element.
        drop_lines = self.drop_lines

        if not drop_lines:
            return

        if drop_lines.line['defined']:

            self._xml_start_tag('c:dropLines')

            # Write the c:spPr element.
            self._write_sp_pr(drop_lines)

            self._xml_end_tag('c:dropLines')
        else:
            self._xml_empty_tag('c:dropLines')

    def _write_overlap(self, val):
        # Write the <c:overlap> element.

        if val is None:
            return

        attributes = [('val', val)]

        self._xml_empty_tag('c:overlap', attributes)

    def _write_num_cache(self, data):
        # Write the <c:numCache> element.
        count = len(data)

        self._xml_start_tag('c:numCache')

        # Write the c:formatCode element.
        self._write_format_code('General')

        # Write the c:ptCount element.
        self._write_pt_count(count)

        # for i (0 .. count - 1):
        #    token = data[i]

            # Write non-numeric data as 0.
            # if (token is not None
            #    and token !~ /^([+-]?)(?=\d|\.\d)\d*(\.\d*)?([Ee]([+-]?\d+))?$/)
            # :
            #    token = 0

            # Write the c:pt element.
            # self._write_pt(i, token)

        self._xml_end_tag('c:numCache')

    def _write_str_cache(self, data):
        # Write the <c:strCache> element.
        count = len(data)

        self._xml_start_tag('c:strCache')

        # Write the c:ptCount element.
        self._write_pt_count(count)

        for i in range(count):
            # Write the c:pt element.
            self._write_pt(i, data[i])

        self._xml_end_tag('c:strCache')

    def _write_format_code(self, data):
        # Write the <c:formatCode> element.

        self._xml_data_element('c:formatCode', data)

    def _write_pt_count(self, val):
        # Write the <c:ptCount> element.

        attributes = [('val', val)]

        self._xml_empty_tag('c:ptCount', attributes)

    def _write_pt(self, idx, value):
        # Write the <c:pt> element.

        if value is None:
            return

        attributes = [('idx', idx)]

        self._xml_start_tag('c:pt', attributes)

        # Write the c:v element.
        self._write_v(value)

        self._xml_end_tag('c:pt')

    def _write_v(self, data):
        # Write the <c:v> element.

        self._xml_data_element('c:v', data)

    def _write_protection(self):
        # Write the <c:protection> element.
        if not self.protection:
            return

        self._xml_empty_tag('c:protection')

    def _write_d_pt(self, points):
        # Write the <c:dPt> elements.
        index = -1

        if not points:
            return

        for point in (points):
            index += 1
            if not point:
                continue

            self._write_d_pt_point(index, point)

    def _write_d_pt_point(self, index, point):
        # Write an individual <c:dPt> element.

            self._xml_start_tag('c:dPt')

            # Write the c:idx element.
            self._write_idx(index)

            # Write the c:spPr element.
            self._write_sp_pr(point)

            self._xml_end_tag('c:dPt')

    def _write_d_lbls(self, labels):
        # Write the <c:dLbls> element.

        if not labels:
            return

        self._xml_start_tag('c:dLbls')

        # Write the c:dLblPos element.
        if labels['position']:
            self._write_d_lbl_pos(labels['position'])

        # Write the c:showVal element.
        if labels['value']:
            self._write_show_val()

        # Write the c:showCatName element.
        if labels['category']:
            self._write_show_cat_name()

        # Write the c:showSerName element.
        if labels['series_name']:
            self._write_show_ser_name()

        # Write the c:showPercent element.
        if labels['percentage']:
            self._write_show_percent()

        # Write the c:showLeaderLines element.
        if labels['leader_lines']:
            self._write_show_leader_lines()

        self._xml_end_tag('c:dLbls')

    def _write_show_val(self):
        # Write the <c:showVal> element.
        val = 1

        attributes = [('val', val)]

        self._xml_empty_tag('c:showVal', attributes)

    def _write_show_cat_name(self):
        # Write the <c:showCatName> element.
        val = 1

        attributes = [('val', val)]

        self._xml_empty_tag('c:showCatName', attributes)

    def _write_show_ser_name(self):
        # Write the <c:showSerName> element.
        val = 1

        attributes = [('val', val)]

        self._xml_empty_tag('c:showSerName', attributes)

    def _write_show_percent(self):
        # Write the <c:showPercent> element.
        val = 1

        attributes = [('val', val)]

        self._xml_empty_tag('c:showPercent', attributes)

    def _write_show_leader_lines(self):
        # Write the <c:showLeaderLines> element.
        val = 1

        attributes = [('val', val)]

        self._xml_empty_tag('c:showLeaderLines', attributes)

    def _write_d_lbl_pos(self, val):
        # Write the <c:dLblPos> element.

        attributes = [('val', val)]

        self._xml_empty_tag('c:dLblPos', attributes)

    def _write_delete(self, val):
        # Write the <c:delete> element.

        attributes = [('val', val)]

        self._xml_empty_tag('c:delete', attributes)

    def _write_c_invert_if_negative(self, invert):
        # Write the <c:invertIfNegative> element.
        val = 1

        if not invert:
            return

        attributes = [('val', val)]

        self._xml_empty_tag('c:invertIfNegative', attributes)

    def _write_axis_font(self, font):
        # Write the axis font elements.

        if not font:
            return

        self._xml_start_tag('c:txPr')
        self._xml_empty_tag('a:bodyPr')
        self._write_a_lst_style()
        self._xml_start_tag('a:p')

        self._write_a_p_pr_rich(font)

        self._write_a_end_para_rpr()
        self._xml_end_tag('a:p')
        self._xml_end_tag('c:txPr')

    def _write_a_latin(self):
        # Write the <a:latin> element.
        attributes = _

        self._xml_empty_tag('a:latin', attributes)

    def _write_d_table(self):
        # Write the <c:dTable> element.
        table = self.table

        if not table:
            return

        self._xml_start_tag('c:dTable')

        if table.horizontal:

            # Write the c:showHorzBorder element.
            self._write_show_horz_border()

        if table.vertical:

            # Write the c:showVertBorder element.
            self._write_show_vert_border()

        if table.outline:

            # Write the c:showOutline element.
            self._write_show_outline()

        if table.show_keys:

            # Write the c:showKeys element.
            self._write_show_keys()

        self._xml_end_tag('c:dTable')

    def _write_show_horz_border(self):
        # Write the <c:showHorzBorder> element.
        attributes = [('val', 1)]

        self._xml_empty_tag('c:showHorzBorder', attributes)

    def _write_show_vert_border(self):
        # Write the <c:showVertBorder> element.
        attributes = [('val', 1)]

        self._xml_empty_tag('c:showVertBorder', attributes)

    def _write_show_outline(self):
        # Write the <c:showOutline> element.
        attributes = [('val', 1)]

        self._xml_empty_tag('c:showOutline', attributes)

    def _write_show_keys(self):
        # Write the <c:showKeys> element.
        attributes = [('val', 1)]

        self._xml_empty_tag('c:showKeys', attributes)

    def _write_error_bars(self, error_bars):
        # Write the X and Y error bars.

        if not error_bars:
            return

        if error_bars.x_error_bars:
            self._write_err_bars('x', error_bars.x_error_bars)

        if error_bars.y_error_bars:
            self._write_err_bars('y', error_bars.y_error_bars)

    def _write_err_bars(self, direction, error_bars):
        # Write the <c:errBars> element.

        if not error_bars:
            return

        self._xml_start_tag('c:errBars')

        # Write the c:errDir element.
        self._write_err_dir(direction)

        # Write the c:errBarType element.
        self._write_err_bar_type(error_bars.direction)

        # Write the c:errValType element.
        self._write_err_val_type(error_bars.type)

        if not error_bars.endcap:

            # Write the c:noEndCap element.
            self._write_no_end_cap()

        if error_bars.type != 'stdErr':

            # Write the c:val element.
            self._write_error_val(error_bars.value)

        # Write the c:spPr element.
        self._write_sp_pr(error_bars)

        self._xml_end_tag('c:errBars')

    def _write_err_dir(self, val):
        # Write the <c:errDir> element.

        attributes = [('val', val)]

        self._xml_empty_tag('c:errDir', attributes)

    def _write_err_bar_type(self, val):
        # Write the <c:errBarType> element.

        attributes = [('val', val)]

        self._xml_empty_tag('c:errBarType', attributes)

    def _write_err_val_type(self, val):
        # Write the <c:errValType> element.

        attributes = [('val', val)]

        self._xml_empty_tag('c:errValType', attributes)

    def _write_no_end_cap(self):
        # Write the <c:noEndCap> element.
        attributes = [('val', 1)]

        self._xml_empty_tag('c:noEndCap', attributes)

    def _write_error_val(self, val):
        # Write the <c:val> element for error bars.

        attributes = [('val', val)]

        self._xml_empty_tag('c:val', attributes)

    def _write_up_down_bars(self):
        # Write the <c:upDownBars> element.
        up_down_bars = self.up_down_bars

        if not up_down_bars:
            return

        self._xml_start_tag('c:upDownBars')

        # Write the c:gapWidth element.
        self._write_gap_width(150)

        # Write the c:upBars element.
        self._write_up_bars(up_down_bars.up)

        # Write the c:downBars element.
        self._write_down_bars(up_down_bars.down)

        self._xml_end_tag('c:upDownBars')

    def _write_gap_width(self, val):
        # Write the <c:gapWidth> element.

        if val is None:
            return

        attributes = [('val', val)]

        self._xml_empty_tag('c:gapWidth', attributes)

    def _write_up_bars(self, bar_format):
        # Write the <c:upBars> element.

        # if (format.line.or is not None format.fill.) is not None:
        if not 'TODO':

            self._xml_start_tag('c:upBars')

            # Write the c:spPr element.
            self._write_sp_pr(bar_format)

            self._xml_end_tag('c:upBars')
        else:
            self._xml_empty_tag('c:upBars')
