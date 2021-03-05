import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


with open('config.json', 'r') as f:
    config = json.load(f)

DTYPES = config['dataset']['dtypes']


def map_description(where, source):
    methodology_map = {}
    methodology_dict = source.to_dict(orient='split')
    for i, code, descr in methodology_dict['data']:
        methodology_map[code] = descr

    replacements_map = {}

    df_codes = where[where['methodology'].notna()]['methodology'].unique()
    for full_code in df_codes:
        if full_code not in replacements_map:
            full_descr = ''

            for code in full_code.split(', '):
                descr = methodology_map[code]
                full_descr += descr + '\n'
            
            full_descr = full_descr.strip()
            replacements_map[full_code] = full_descr

    where['methodology'] = where['methodology'].replace(replacements_map)


def unmap_description(where, source):
    methodology_map = {}
    methodology_dict = source.to_dict(orient='split')
    for i, code, descr in methodology_dict['data']:
        methodology_map[descr] = code
    
    replacements_map = {}

    df_descripts = where[where['methodology'].notna()]['methodology'].unique()
    for full_descr in df_descripts:
        if full_descr not in replacements_map:
            full_code = ''

            for descr in full_descr.split('\n'):
                code = methodology_map[descr]
                full_code += code + ', '
            
            full_code = full_code.strip()
            full_code = full_code[:-1]
            replacements_map[full_descr] = full_code

    where['methodology'] = where['methodology'].replace(replacements_map)


def show_lineplot(df, ncols=4, width=22, row_height=4, hue=None, style=None, fixed=None, legend=None):
    indicator = df['indicator_name'].unique()[0]
    unit = df['indicator_unit'].unique()[0]
    objects_num = df['object_name'].nunique()
    
    nrows = 0
    if objects_num % ncols == 0:
        nrows = int(objects_num / ncols)
    else:
        nrows = int(objects_num // ncols + 1)
    
    width = width
    height = nrows * row_height
    
    fig, axes = plt.subplots(figsize=(width, height), ncols=ncols, nrows=nrows)
    
    if objects_num % ncols != 0:
        empty_axes_num = ncols - objects_num % ncols
        switch_off = empty_axes_num
        while switch_off > 0:
            row = nrows - 1
            col = ncols - switch_off
            try:
                axes[row, col].axis('off')
            except IndexError:
                axes[col].axis('off')
            switch_off -= 1
    
    title = ''
    fixed_category = ''
    if isinstance(fixed, str):
        category_list = df[fixed].unique()
        category_list = [str(i) for i in category_list]
        fixed_category += fixed + ': '
        fixed_category += ', '.join(category_list)
    elif isinstance(fixed, list):
        for col in fixed:
            category_list = df[col].unique()
            category_list = [str(i) for i in category_list]
            fixed_category += col + ': '
            fixed_category += ', '.join(category_list)
            fixed_category += '; '
        fixed_category = fixed_category[:-2]  # удаляем последнюю "; "
    if fixed is None:
        fig.suptitle(f'{indicator}', fontsize=16)
    else:
        fig.suptitle(f'{indicator} ({fixed_category})', fontsize=16)

    if ncols == 1 & nrows == 1:
        axes_flat = [axes]
    else:
        axes_flat = axes.flat
    
    for object_name, ax in zip(df['object_name'].unique(), axes_flat):
        sns.lineplot(data=df[df['object_name'] == object_name],
                     x='year',
                     y='indicator_value',
                     hue=hue,
                     style=style,
                     ax=ax,
                     legend=legend,
                     markers=True)

        ax.set_title(f'{object_name}')
        ax.set_xlabel('год')
        ax.set_ylabel(f'{unit}')
        ax.grid(True)
        
        if legend is not None:
            ax.legend(loc='upper left')
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.98])
    plt.show()
