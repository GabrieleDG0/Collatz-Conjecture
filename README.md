# Collatz Conjecture Visualiser
This project implements a Collatz visualiser in Python that compute the Collatz sequence for any given integer, create an interactive step-by-step animation, including some statistics 
and show the results on a linear/log scale. Finally allows you to export the final result in png or csv.
<br>

**Note: you can find an .exe file on the Release section if ou want to try the project!**

<br>
<img width="1360" height="723" alt="image" src="https://github.com/user-attachments/assets/60ad4e61-2c37-4167-80f5-96b0457cdcae" />

## Introduction
The Collatz conjecture, also known as the **3n+1 problem**, is a simple but unsolved problem in mathematics. 
It was first proposed by **Lothar Collatz** in 1937 and later studied independently by mathematicians such as Stanislaw Ulam, who gave it names such as the “Ulam conjecture” or the “Hailstone problem” 
Despite its apparent simplicity, the conjecture has resisted a formal proof for over eighty years, making it a fascinating topic for both amateur and professional mathematicians.

## Historical context
The conjecture defines a sequence for any positive integer n by the following rules: if n is even, the next term is n/2; if n is odd, the next term is 3n+1. 
Repeating this process generates a sequence that is conjectured to always reach 1, no matter the starting value. Mathematically:
<p align="center">
<img width="293" height="89" alt="image" src="https://github.com/user-attachments/assets/c9d132e9-0d34-4342-95d4-1b8a7202a472" />
</p>
Iterating f generates the Collatz sequence for any output n. 
Collatz first proposed it in 1937, but Ulam popularized it in the 1960s, emphasizing the seemingly chaotic and unpredictable paths of the sequences. 
Despite numerous computational verifications (checking numbers up to 
2^68 or higher), no general proof or counterexample has been found.   

<br> 
<br>

Historically, the problem attracted the attention of **Stanislaw Ulam** in the 1960s, who proposed a probabilistic perspective and treated the sequences as a stochastic process. 
Although this approach did not provide a solution, it opened the way to studying the statistical behaviour of Collatz sequences. 
Later, in 2010, **Jeffrey Lagarias** highlighted the extreme difficulty of the problem by formalising it in the framework of generalised 3x+1 functions 
and emphasising its deep connections to number theory and combinatorial analysis.

A significant recent advance comes from **Terence Tao** in 2019, who used analytic and probabilistic methods to prove that “almost all” Collatz sequences 
eventually reach values that are “almost bounded", providing a strong proof of the conjecture in a strict probabilistic sense. 
Although this is not a complete proof, it is a big step forward in understanding the problem.

Modern approaches combine large-scale computational testing with probabilistic and analytical techniques to study the typical behaviour of sequences.
The simplicity of this function belies the complexity of the sequences it generates, where slight changes to the initial value can lead to very different paths, a property of chaotic systems.

## Implementation
This project implements a Collatz visualiser in Python using Tkinter and Matplotlib. 
The software allows the user to generate sequences either by entering a specific number or by random selection. 
Each sequence can be animated step-by-step to show the evolution of the values and their operations (n/2 or 3n+1) in real time. 
Users can pause, resume or manually navigate through the sequence and switch the y-axis of the graph between **linear** and **logarithmic scale** to better visualise large or small values.
The main chart highlights the current sequence step with a prominent marker and supports interactive hovering via mplcursors, displaying step number and value. 
The number 25 on a log and linear scale:

<img width="2869" height="1389" alt="Collatz-Conjecture-N-25" src="https://github.com/user-attachments/assets/ca87d230-e18c-4b36-845c-ac0368989de8" />
<img width="2872" height="1389" alt="Collatz-Conjecture-N-25-linear" src="https://github.com/user-attachments/assets/f0e78cd4-0dd6-4303-8c88-e93e24a48e95" />

The panels on the left provide statistical information, including start number, sequence length, maximum value and a dynamic list of all sequence elements, with colour highlighting for both the current and selected point.
The export function allows you to save both the visualised diagram as a PNG and the numerical sequence as a CSV or text file. 
The "Read More" button opens the Collatz Wikipedia page for theoretical references.

<img width="960" height="540" alt="image" src="https://github.com/user-attachments/assets/a867cac4-acc3-49ec-9f34-97c955134ad7" />

## Further reading
This software bridges mathematics, and computational analysis, making it suitable for everyone interested in number theory and dynamical systems.
If you want to learn more about the Conjecture, here's a few useful links:
- Wikipedia: [Collatz_Conjecture](https://en.wikipedia.org/wiki/Collatz_conjecture)
- Jeffrey Lagarias: [The_3x+1_and_its_generalizations](https://web.williams.edu/Mathematics/sjmiller/public_html/383Fa21/addcomments/Lagarias_3x+1AndItsGeneralizations.pdf)
- Jeffrey Lagarias: [The 3x+1 Problem: An Overview](https://arxiv.org/pdf/2111.02635)
- Terence Tao: [The_notorious_Collatz_Conjecture](https://terrytao.wordpress.com/wp-content/uploads/2020/02/collatz.pdf)
- Terence Tao: [Almost all Collatz orbits attain almost bounded values](http://arxiv.org/pdf/1909.03562)
## Contributions
If you find any bugs or errors, feel free to open an issue!
