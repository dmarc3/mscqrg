import os
import json

from tabulate import tabulate

from mscqrg.load_datatypes import get_cards

DIR = os.path.dirname(__file__)
PDF_PATH = os.path.join(DIR, "MSC_Nastran_2022.4_Quick_Reference_Guide.pdf")
URL = "https://help.hexagonmi.com/bundle/MSC_Nastran_2022.4/page/Nastran_Combined_Book/qrg/"
# https://help.hexagonmi.com/bundle/MSC_Nastran_2022.4/page/Nastran_Combined_Book/qrg/bulkab/TOC.ABINFL.xhtml
BROWSER = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe %s"

class BULK_DATA:
    """Bulk Data Entry documentation reader
    """
   
    def __init__(self, name: str, pdf=False):
        """Initialization method for BULK_DATA class

        Args:
            name (str): Bulk data entry name (i.e. CBUSH, CQUAD4, etc.)
            pdf (bool, optional): Flag to enforce read by PDF. If False, read from JSON if it exists. Defaults to False.
        """
        self.name = name.upper()
        self.short_description = ''
        self.long_description = ''
        self.format = []
        self.fields = []
        self._page = 0
        if self.name in get_cards():
            self._set_url()
            if pdf or not os.path.exists(os.path.join(DIR, 'BULK', self.name+'.json')):
                self.load_from_pdf()
                if not os.path.exists(os.path.join(DIR, 'BULK', self.name+'.json')):
                    self.export_json()
            else:
                self.load_from_json()

    def __repr__(self) -> str:
        """String representation method

        Returns:
            str: Representation string
        """
        logic = (self.short_description and self.long_description and self.format and self.fields)
        if logic:
            line_break = ['-'*100]
            header = ['__**[`'+self.name+'`]('+self.url+')**__'+':  '+self.short_description]
            description = [self.long_description]
            format = self._str_format()
            fields = self._str_fields()
            out = '\n\n'.join(header + line_break +
                              description + line_break +
                              format + line_break +
                              fields)
            return out
        else:
            return ''

    def _set_url(self):
        """Builds Hexagon QRG URL for given bulk data entry
        """
        chars = self.name[0]
        if chars == "C":
            chars = chars = self.name[:2]

        if chars in ['A', 'B']:
            bulk = 'bulkab'
        elif chars in ['CA', 'CB', 'CC', 'CD', 'CE', 'CF', 'CG', 'CH', 'CI', 'CJ', 'CK', 'CL', 'CM', 'CN']:
            bulk = 'bulkc1'
        elif chars in ['CO', 'CP', 'CQ', 'CR', 'CS', 'CT', 'CU', 'CV', 'CW', 'CX', 'CY', 'CZ']:
            bulk = 'bulkc2'
        elif chars in ['D', 'E']:
            bulk = 'bulkde'
        elif chars in ['F', 'G', 'H', 'I', 'J', 'K', 'L']:
            bulk = 'bulkfgil'
        elif chars in ['M', 'N', 'O']:
            bulk = 'bulkmno'
        elif chars in ['P']:
            bulk = 'bulkp'
        elif chars in ['Q', 'R', 'S']:
            bulk = 'bulkqrs'
        elif chars in ['T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
            bulk = 'bulktuv'

        self.url = URL + bulk +'/TOC.' + self.name + '.xhtml'

    def _read_pdf(self) -> list:
        """Read and Parse PDF documentation for desired Bulk Data Entry.

        Raises:
            ValueError: Requested Bulk Data Entry was not found

        Returns:
            list: Raw PDF text for desired Bulk Data Entry
        """
        import fitz
        with fitz.open(PDF_PATH) as doc:
            # Get page numbers of interest
            toc = doc.get_toc()
            for i, section in enumerate(toc):
                if section[1] == self.name:
                    break
            self._page = toc[i][2]
            if i == len(toc)-1:
                raise ValueError(self.name+' not found within documentation.')
            # Get raw page data
            pages = []
            for page in doc.pages(section[2]-1, toc[i+1][2]-1, 1):
                text = page.get_text("dict")
                text['blocks'] = sorted(text['blocks'], key=lambda d: d['bbox'][1])
                pages.append(text['blocks'][1:-3])
            # Get raw text data
            text = []
            found_card = True
            for sections in pages:
                for section in sections:
                    tmp = []
                    if 'lines' in section:
                        for line in section['lines']:
                            for span in line['spans']:
                                if span['text'] == self.name:
                                    found_card = not found_card
                                if found_card:
                                    if len(span['text']) > 8:
                                        for item in span['text'].split():
                                            tmp.append(item)
                                    else:
                                        tmp.append(span['text'])
                                else:
                                    tmp.append(span['text'])
                        text.append(tmp)
        return text

    def _find_indeces(self, text: list) -> list:
        """Identifies indeces for Example, Describer, and Remarks section of Bulk Data Entry documentation

        Args:
            text (list): Raw PDF text for desired Bulk Data Entry

        Returns:
            list: List containing indeces of Example, Describer, and Remarks sections
        """
        # Find Example index
        i = 0
        while 'Example' not in text[i][0]:
            i+=1
        example = i
        # Find Describer index
        while 'Describer' not in text[i][0]:
            i+=1
        describer = i
        # Find Remarks index
        while 'Remarks' not in text[i][0]:
            i+=1
        remarks = i
        return [example, describer, remarks]

    def _str_format(self) -> str:
        """Method to format Bulk Data Entry Format table into string

        Returns:
            str: Bulk Data Entry Format table
        """
        if self.format:
            str_format = []
            count = 0
            for row in self.format:
                if len(row) == 1:
                    count += 1
                    str_format.extend(row)
            str_format.append('```text\n\nFormat:\n' + 
                               tabulate(
                                   self.format[count:],
                                   headers='firstrow',
                                   tablefmt='markdown',
                               ) + '\n\n\n```')
            return str_format
            # ['Format:', '```text\n'+]
            # return tabulate(
            #     self.format,
            #     headers='firstrow',
            #     tablefmt='markdown',
            #     # tablefmt='fancy_grid',
            # )
        else:
            return ''
    
    def _str_fields(self):
        """Method to format Bulk Data Entry Describer/Meaning table into string

        Returns:
            str: Bulk Data Entry Describer/Meaning table
        """
        if self.fields:
            return ['```text\n\n' + tabulate(
                self.fields,
                headers='firstrow',
                tablefmt='markdown',
                maxcolwidths=107,
                # maxcolwidths=self._get_max_field_cols(),
            ) + '\n\n\n```']
        else:
            return []
    
    def _get_max_field_cols(self) -> list:
        """Determines size of string tables

        Returns:
            list: List containing maximum column widths for Describer/Meaning table
        """
        maxcols = [len(self.fields[0][0]), len(self.fields[0][1])]
        # try:
        #     term_dim = os.get_terminal_size()
        #     for ind in range(len(self.fields)):
        #         maxcols[0] = max(maxcols[0], len(self.fields[ind][0]))
        #         maxcols[1] = max(maxcols[1], len(self.fields[ind][1]))
        #     buffer = 20
        #     if maxcols[1] > term_dim.columns - buffer:
        #         maxcols[1] = term_dim.columns - maxcols[0] - buffer
        # except OSError:
        #     pass
        return maxcols

    def _reformat_format(self, table: list) -> list:
        """Adjust Bulk Data Entry Format table spacing/formatting

        Args:
            table (list): Raw format text from Bulk Data Entry PDF read

        Returns:
            list: Update text from Bulk Data Entry PDF read with corrected spacing/formatting
        """
        # Make left adjust with 8 character spacing
        count = 0
        while len(table[count]) == 1:
            count += 1
        for ind, row in enumerate(table[count:]):
            table[count+ind] = [field.ljust(8) for field in row]
            if count+ind > count+1:
                table[count+ind] = [''] + table[count+ind]
        return table

    def _reformat_describer(self, table: list) -> list:
        """Adjust Bulk Data Entry Describer/Meaning table spacing/formatting

        Args:
            table (list): Raw Describer/Meaning text from Bulk Data Entry PDF read

        Returns:
            list: Update text from Bulk Data Entry PDF read with corrected spacing/formatting
        """
        # Remove duplicate headers (if spanning multiple pages)
        while ['Describer', 'Meaning'] in table[1:]:
            ind = table.index(['Describer', 'Meaning'], 2)
            del table[ind]
        # Combine entries and calculate maximum column widths
        maxcols = [len(table[0][0]), len(table[0][1])]
        for ind, row in enumerate(table):
            table[ind] = [row[0]] + [''.join(row[1:])]
            maxcols[0] = max(maxcols[0], len(table[ind][0]))
            maxcols[1] = max(maxcols[1], len(table[ind][1]))
        while ['v','v'] in table:
            ind = table.index(['v','v'])
            del table[ind]
        while ['v', ''] in table:
            ind = table.index(['v',''])
            del table[ind]
        # dims = os.get_terminal_size()
        # if maxcols[1] > dims.columns:
        #     maxcols[1] = dims.columns - maxcols[0] - 7
        return table

    def load_from_pdf(self):
        """Method to read attributes from PDF documentation.
        """
        try:
            text = self._read_pdf()
            self.short_description = text[0][1]
            self.long_description = text[1][0]
            example, describer, remarks = self._find_indeces(text)
            self.format = self._reformat_format(text[3:example])
            self.fields = self._reformat_describer(text[describer:remarks])
        except ValueError:
            print(self.name+' not found in documentation. Check Nastran Bulk Data Entry spelling.')

    def load_from_json(self):
        """Method to read attributes from JSON.
        """
        with open(os.path.join(DIR, 'BULK', self.name+'.json'), 'r') as f:
            data = json.load(f)
        self.short_description = data['short_description']
        self.long_description = data['long_description']
        self.format = data['format']
        self.fields = data['fields']

    def export_json(self):
        """Export class attributes to json file
        """
        if not os.path.exists(os.path.join(DIR,'BULK')):
            os.mkdir(os.path.join(DIR,'BULK'))
        out = dict(
            name=self.name,
            short_description=self.short_description,
            long_description=self.long_description,
            format=self.format,
            fields=self.fields,
        )
        with open(os.path.join(DIR, 'BULK', self.name+'.json'), 'w') as f:
            json.dump(out, fp=f)
    
    def open_pdf(self):
        path = "file://"+os.path.abspath(PDF_PATH)+"#page="+str(self._page)
        import webbrowser
        browser = webbrowser.get(BROWSER)
        browser.open(path)
        # os.system("start "+path)
