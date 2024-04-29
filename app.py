from flask import Flask, render_template, request
import matplotlib
matplotlib.use('Agg')  # This ensures matplotlib uses a non-GUI backend
import matplotlib.pyplot as plt
from classy import Class
import numpy as np
import io
import base64

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    default_params = {
        'omega_b': 0.0224,
        'omega_cdm': 0.12,
        'h': 0.67,
        'A_s': 2.3e-9,
        'n_s': 0.96,
        'tau_reio': 0.07,
        'output': 'tCl pCl lCl',
        'modes': 's',
        'lensing': 'yes',
        'l_max_scalars': 2500,
    }

    if request.method == 'POST':
        # Update parameters with values from the form
        for key in default_params.keys():
            if key in request.form and request.form[key]:
                try:
                    default_params[key] = float(request.form[key])
                except ValueError:
                    pass  # Handle the exception if the conversion fails

    # Generate the plot with either default or updated parameters
    plot_url = generate_plot(default_params)

    return render_template('index.html', plot_url=plot_url, params=default_params)

def generate_plot(params):
    cosmo = Class()
    cosmo.set(params)
    cosmo.compute()
    cls = cosmo.lensed_cl(params['l_max_scalars'])
    ell = cls['ell']
    cl_TT = cls['tt']

    start_index = np.where(ell >= 2)[0][0]  # Ensure the plot starts from ell >= 2
    ell = ell[start_index:]
    cl_TT = cl_TT[start_index:]

    plt.figure(figsize=(8, 6))
    plt.plot(ell, ell * (ell + 1) * cl_TT * 1e12)
    plt.xlabel('$\ell$')
    plt.ylabel('$\ell(\ell+1)C_\ell^\mathrm{TT} \, [\mu K^2]$')
    plt.title('CMB TT Power Spectrum')
    plt.xscale('log')
    plt.grid(True)

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf-8')

    plt.close()  # Close the plot to free up memory
    cosmo.struct_cleanup()
    cosmo.empty()

    return 'data:image/png;base64,{}'.format(plot_url)

if __name__ == '__main__':
    app.run(debug=True)
