<div align=center>
<h1>HLA Curation Interface</h1>

[Production Site](https://hci.clinicalgenome.org/) |
[Test Site](https://hci-test.clinicalgenome.org/) |
[Developer Documentation](https://hla-curation-interface.readthedocs.io/latest/index.html)

![continuous integration](https://github.com/clingen/hla-curation-interface/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/ClinGen/hla-curation-interface/graph/badge.svg?token=23NGX9GT02)](https://codecov.io/gh/ClinGen/hla-curation-interface)
![docs](https://readthedocs.org/projects/hla-curation-interface/badge/?version=latest)
</div>

The HLA Curation Interface (HCI) is a tool designed to facilitate the curation of
information about HLA alleles and haplotypes.

The HCI is maintained by the Stanford contingent of
[ClinGen](https://clinicalgenome.org).

## Getting Started

- Install [uv](https://github.com/astral-sh/uv).
- Clone the repository.
- Install dependencies: `uv sync`.
- Install [just](https://github.com/casey/just).
- Create and populate a `.env` file in the root of the repository.
- Run the development server: `just django-runserver`.

## Documentation

The developer documentation for the HCI is hosted on Read the Docs
[here](https://hla-curation-interface.readthedocs.io/latest/index.html).

- [Tutorials](https://hla-curation-interface.readthedocs.io/latest/tutorials.html)
- [How-To Guides](https://hla-curation-interface.readthedocs.io/latest/how-to-guides.html)
- [Explanations](https://hla-curation-interface.readthedocs.io/latest/explanations.html)
- [Reference Guides](https://hla-curation-interface.readthedocs.io/latest/reference-guides.html)

## Contributing

You are welcome to submit a
[bug report](https://github.com/clingen/hla-curation-interface/issues/new)
or a [pull request](https://github.com/ClinGen/hla-curation-interface/compare).

## License

The HCI's source code is subject to the MIT License. Read the text of the license
[here](./LICENSE.md).
