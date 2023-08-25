sensor_defs = [
    {
        "criteria": {
            "Image Make": "Sentera",
            "Image Model": "2102",
            "EXIF LensModel": "5.4mm-0001_0016",
        },
        "settings": {
            "sensor": "D4K_NarrowNDRE",
            "cal_in_path": False,
            "independent_ils": False,
        },
        "bands": [("rededge", [1.0, 0.0, -0.956], 0), 
                ("nir", [-0.341, 0.0, 2.426], 2)],
    },
    {
        "criteria": {
            "Image Make": "Sentera",
            "Image Model": "2102",
            "EXIF LensModel": "5.4mm-0001_0014",
        },
        "settings": {
            "sensor": "D4K_NarrowRGB",
            "cal_in_path": False,
            "independent_ils": False,
        },
        "bands": [
            ("red", [1.0, 0.0, 0.0], 0),
            ("green", [0.0, 1.0, 0.0], 1),
            ("blue", [0.0, 0.0, 1.0], 2),
        ],
    }]

sensor_bands_defs = {
  "RGB":  [
            ("red", [1.0, 0.0, 0.0], 0),
            ("green", [0.0, 1.0, 0.0], 1),
            ("blue", [0.0, 0.0, 1.0], 2),
        ],
  "NIR":  [
            ("rededge", [1.0, 0.0, -0.956], 0), 
            ("nir", [-0.341, 0.0, 2.426], 2)
        ]}

a = """
    <Camera:BandName>
        <rdf:Seq>
          <rdf:li>Red</rdf:li>
          <rdf:li>Green</rdf:li>
          <rdf:li>Blue</rdf:li>
        </rdf:Seq>
      </Camera:BandName>
      <Camera:CentralWavelength>
        <rdf:Seq>
          <rdf:li>650</rdf:li>
          <rdf:li>548</rdf:li>
          <rdf:li>446</rdf:li>
        </rdf:Seq>
      </Camera:CentralWavelength>
      <Camera:WavelengthFWHM>
        <rdf:Seq>
          <rdf:li>70</rdf:li>
          <rdf:li>45</rdf:li>
          <rdf:li>60</rdf:li>
        </rdf:Seq>
      </Camera:WavelengthFWHM>
      <Camera:ColorTransform>
        <rdf:Seq>
          <rdf:li>1.150</rdf:li>
          <rdf:li>-0.110</rdf:li>
          <rdf:li>-0.034</rdf:li>
          <rdf:li>-0.329</rdf:li>
          <rdf:li>1.421</rdf:li>
          <rdf:li>-0.199</rdf:li>
          <rdf:li>-0.061</rdf:li>
          <rdf:li>-0.182</rdf:li>
          <rdf:li>1.377</rdf:li>
        </rdf:Seq>
"""