from flask import Flask, render_template, request
import matplotlib
matplotlib.use('Agg')  # This needs to be done before importing pyplot
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
    }
    if request.method == 'POST':
        try:
            params = {
                'output': 'tCl pCl lCl',
                'modes': 's',
                'lensing': 'yes',
                'l_max_scalars': 2500,
                'omega_b': float(request.form.get('omega_b', default_params['omega_b'])),
                'omega_cdm': float(request.form.get('omega_cdm', default_params['omega_cdm'])),
                'h': float(request.form.get('h', default_params['h'])),
                'A_s': 2.3e-9,
                'n_s': 0.96,
                'tau_reio': 0.07,
            }
            plot_url = generate_plot(params)
            # Update default params to reflect submitted values
            default_params.update(params)
        except Exception as e:
            print(f"Error: {e}")
            plot_url = None
    else:
        plot_url = None
    return render_template('index.html', plot_url=plot_url, params=default_params)


def generate_plot(params):
    cosmo = Class()
    cosmo.set(params)
    cosmo.compute()
    cls = cosmo.lensed_cl(params['l_max_scalars'])
    ell = cls['ell']
    cl_TT = cls['tt']

    start_index = np.where(ell >= 2)[0][0]
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

    cosmo.struct_cleanup()
    cosmo.empty()

    return 'data:image/png;base64,{}'.format(plot_url)

if __name__ == '__main__':
    app.run(debug=True)
