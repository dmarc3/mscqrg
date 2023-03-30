import fitz
import os
import sys
import tabulate

PDF_PATH = "MSC_Nastran_2022.4_Quick_Reference_Guide.pdf"
dims = os.get_terminal_size()
COLS = dims.columns

def reformat_format(table: list) -> list:
    # Make left adjust with 8 character spacing
    for ind, row in enumerate(table):
        table[ind] = [field.ljust(8) for field in row]
        if ind > 1:
            table[ind] = [''] + table[ind]
    return table

def reformat_describer(table: list, remarks: int) -> list:
    # Remove duplicate headers (if spanning multiple pages)
    while ['Describer', 'Meaning'] in table[1:]:
        ind = table.index(['Describer', 'Meaning'], 2)
        del table[ind]
        remarks -= 1
    # Combine entries and calculate maximum column widths
    maxcols = [len(table[0][0]), len(table[0][1])]
    for ind, row in enumerate(table):
        table[ind] = [row[0]] + [''.join(row[1:])]
        maxcols[0] = max(maxcols[0], len(table[ind][0]))
        maxcols[1] = max(maxcols[1], len(table[ind][1]))
    while ['v','v'] in table:
        ind = table.index(['v','v'])
        del table[ind]
        remarks -= 1
    while ['v', ''] in table:
        ind = table.index(['v',''])
        del table[ind]
        remarks -= 1
    if maxcols[1] > COLS:
        maxcols[1] = COLS - maxcols[0] - 7
    return table, remarks, maxcols

def main(card):
    with fitz.open(PDF_PATH) as doc:
        toc = doc.get_toc()
        for i, section in enumerate(toc):
            if section[1] == card:
                break
        pages = []
        for page in doc.pages(section[2]-1, toc[i+1][2]-1, 1):
            pix = page.get_pixmap()
            imgname = "page-%i.png" % page.number 
            pix.save(imgname)
            # os.startfile(imgname)
            text = page.get_text("dict")
            text['blocks'] = sorted(text['blocks'], key=lambda d: d['bbox'][1])
            bbox = []
            img = mpimg.imread(imgname)
            imgplot = plt.imshow(img)
            ax = plt.gca()
            for val in text['blocks']:
                rect = Rectangle(
                    val['bbox'][:2],
                    val['bbox'][2]-val['bbox'][0],
                    val['bbox'][3]-val['bbox'][1],
                    linewidth=1,
                    edgecolor='r',
                    facecolor='none',
                    )
                ax.add_patch(rect)
                bbox.append(val['bbox'])
            pages.append(text['blocks'][1:-3])
            # text['blocks'][0]['lines'][0]['spans'][0]['text']
            # plt.show()

        text = []
        for sections in pages:
            for section in sections:
                tmp = []
                for line in section['lines']:
                    for span in line['spans']:
                        tmp.append(span['text'])
                text.append(tmp)
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
        # Print card and short description
        print('\n'+':  '.join(text[0])+'\n')
        # Print long description
        print(''.join(text[1])+'\n')
        # Print card format
        print(text[2][0])
        text[3:example] = reformat_format(text[3:example])
        out = tabulate.tabulate(
            text[3:example],
            headers='firstrow',
            tablefmt='fancy_grid',
        )
        print(out+'\n')
        # Print describer table
        text[describer:remarks], remarks, maxcols = reformat_describer(text[describer:remarks], remarks)
        out = tabulate.tabulate(
            text[describer:remarks],
            headers='firstrow',
            tablefmt='fancy_grid',
            maxcolwidths=maxcols,
        )
        print(out+'\n')

if __name__ == "__main__":
    from bulk_data import BULK_DATA
    entry = BULK_DATA(sys.argv[1])
    print(entry)