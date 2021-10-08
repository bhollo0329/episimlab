from episimlab.models import PartitionV1

def main():
    model = PartitionV1()
    in_ds = model.get_in_ds()
    in_ds['setup_sto__sto_toggle'] = 0
    model.out_ds = result = in_ds.xsimlab.run(model=model)
    state = result['compt_model__state']
    model.plot()


if __name__ == '__main__':
	main()