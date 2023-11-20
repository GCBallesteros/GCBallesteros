<div align="center"> <img src="./banner/horizon_man_looking_hypercube/banner.gif" loop=infinite> </div>

I'm a Data Scientist and Scientific Software Developer with a knack for
optimization. I enjoy it the most when I work where engineering and software
development intersect. In my free time you will find me learning new
programming languages, implementing fancy algorithms, playing music, enjoying
nature and tweaking my neovim config.

Currently I'm a Data Scientist (and more) @ [Kuva Space](www.kuvaspace.com)
helping build a constellation of hyperspectral cubesats

- Other places to find me:
  - 🌐 Blog: [Maxwell Rules](https://www.maxwellrules.com)
  - 🎓 Publications: [Google Scholar](https://scholar.google.co.uk/citations?hl=es&user=ky87HY0AAAAJ&view_op=list_works&sortby=pubdate)
  - 📧 dev &lt;at&gt; maxwellrules.com

### Open Source Projects 

Total ⭐: {{total_stars}}

#### Scientific algorithms (Σ⭐={{science_stars}})
  {% for repo in science_repos -%}
  - [{{repo.name}}](https://www.github.com/{{repo.owner}}/{{repo.name}}) (⭐ {{repo.stars}}): {{badges[repo.lang]}} {{repo.description}}
  {% endfor -%}
  - ... and more

#### Neovim (Σ⭐={{vim_stars}})
  {% for repo in vim_repos -%}
  - [{{repo.name}}](https://www.github.com/{{repo.owner}}/{{repo.name}}) (⭐ {{repo.stars}}): {{badges[repo.lang]}} {{repo.description}}
  {% endfor -%}
  - ... and more
