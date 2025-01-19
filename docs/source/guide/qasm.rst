OpenQASM 2.0支持
====================


单比特量子逻辑门：
`````````````````````````````````````````````````
.. tabularcolumns:: |m{0.06\textwidth}<{\centering}|c|c|

.. list-table:: 
   :align: center
   :class: longtable 

   * - |I|                                                     
     - ``I``                     
     - :math:`\begin{bmatrix} 1 & 0 \\ 0 & 1 \end{bmatrix}\quad`
   * - |H|                                                      
     - ``Hadamard``              
     - :math:`\begin{bmatrix} 1/\sqrt {2} & 1/\sqrt {2} \\ 1/\sqrt {2} & -1/\sqrt {2} \end{bmatrix}\quad`
   * - |T|                                                     
     - ``T``                     
     - :math:`\begin{bmatrix} 1 & 0 \\ 0 & \exp(i\pi / 4) \end{bmatrix}\quad`
   * - |S|                                                     
     - ``S``                      
     - :math:`\begin{bmatrix} 1 & 0 \\ 0 & 1i \end{bmatrix}\quad`
   * - |X|                                                     
     - ``Pauli-X``               
     - :math:`\begin{bmatrix} 0 & 1 \\ 1 & 0 \end{bmatrix}\quad`
   * - |Y|                                                     
     - ``Pauli-Y``               
     - :math:`\begin{bmatrix} 0 & -1i \\ 1i & 0 \end{bmatrix}\quad`
   * - |Z|                                                     
     - ``Pauli-Z``               
     - :math:`\begin{bmatrix} 1 & 0 \\ 0 & -1 \end{bmatrix}\quad`
   * - |X1|                                                    
     - ``X1``                    
     - :math:`\begin{bmatrix} 1/\sqrt {2} & -1i/\sqrt {2} \\ -1i/\sqrt {2} & 1/\sqrt {2} \end{bmatrix}\quad`
   * - |Y1|                                                    
     - ``Y1``                    
     - :math:`\begin{bmatrix} 1/\sqrt {2} & -1/\sqrt {2} \\ 1/\sqrt {2} & 1/\sqrt {2} \end{bmatrix}\quad`
   * - |Z1|                                                    
     - ``Z1``                    
     - :math:`\begin{bmatrix} \exp(-i\pi/4) & 0 \\ 0 & \exp(i\pi/4) \end{bmatrix}\quad`
   * - |RX|                                                    
     - ``RX``                    
     - :math:`\begin{bmatrix} \cos(\theta/2) & -1i×\sin(\theta/2) \\ -1i×\sin(\theta/2) & \cos(\theta/2) \end{bmatrix}\quad`
   * - |RY|                                                    
     - ``RY``                    
     - :math:`\begin{bmatrix} \cos(\theta/2) & -\sin(\theta/2) \\ \sin(\theta/2) & \cos(\theta/2) \end{bmatrix}\quad`
   * - |RZ|                                                    
     - ``RZ``                    
     - :math:`\begin{bmatrix} \exp(-i\theta/2) & 0 \\ 0 & \exp(i\theta/2) \end{bmatrix}\quad`
   * - |U1|                                                    
     - ``U1``                    
     - :math:`\begin{bmatrix} 1 & 0 \\ 0 & \exp(i\theta) \end{bmatrix}\quad`
   * - |U2|                                                    
     - ``U2``                    
     - :math:`\begin{bmatrix} 1/\sqrt {2} & -\exp(i\lambda)/\sqrt {2} \\ \exp(i\phi)/\sqrt {2} & \exp(i\lambda+i\phi)/\sqrt {2} \end{bmatrix}\quad`
   * - |U3|                                                    
     - ``U3``                    
     - :math:`\begin{bmatrix} \cos(\theta/2) & -\exp(i\lambda)×\sin(\theta/2) \\ \exp(i\phi)×\sin(\theta/2) & \exp(i\lambda+i\phi)×\cos(\theta/2) \end{bmatrix}\quad`
   * - |U4|                                                    
     - ``U4``                    
     - :math:`\begin{bmatrix} u0 & u1 \\ u2 & u3 \end{bmatrix}\quad`


多比特量子逻辑门：
`````````````````````````````````````````````````
.. tabularcolumns:: |m{0.1\linewidth}<{\centering}|c|c|

.. list-table:: 
   :widths: auto
   :align: center
   :class: longtable 

   * - |CNOT|                                                      
     - ``CNOT``                  
     - :math:`\begin{bmatrix} 1 & 0 & 0 & 0  \\ 0 & 1 & 0 & 0 \\ 0 & 0 & 0 & 1 \\ 0 & 0 & 1 & 0 \end{bmatrix}\quad`
   * - |CR|                                                        
     - ``CR``                    
     - :math:`\begin{bmatrix} 1 & 0 & 0 & 0  \\ 0 & 1 & 0 & 0 \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & \exp(i\theta) \end{bmatrix}\quad`
   * - |iSWAP|                                                      
     - ``iSWAP``                 
     - :math:`\begin{bmatrix} 1 & 0 & 0 & 0  \\ 0 & \cos(\theta) & i×\sin(\theta) & 0 \\ 0 & i×\sin(\theta) & \cos(\theta) & 0 \\ 0 & 0 & 0 & 1 \end{bmatrix}\quad`
   * - |SWAP|                                                      
     - ``SWAP``                  
     - :math:`\begin{bmatrix} 1 & 0 & 0 & 0  \\ 0 & 0 & 1 & 0 \\ 0 & 1 & 0 & 0 \\ 0 & 0 & 0 & 1 \end{bmatrix}\quad`
   * - |CZ|                                                        
     - ``CZ``                    
     - :math:`\begin{bmatrix} 1 & 0 & 0 & 0  \\ 0 & 1 & 0 & 0 \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & -1 \end{bmatrix}\quad`
   * - |CU|                                                        
     - ``CU``                    
     - :math:`\begin{bmatrix} 1 & 0 & 0 & 0  \\ 0 & 1 & 0 & 0 \\ 0 & 0 & u0 & u1 \\ 0 & 0 & u2 & u3 \end{bmatrix}\quad`
   * - |RXX|                                                        
     - ``RXX``
     - :math:`\begin{bmatrix} \cos(\theta/2) & 0 & 0 & -i\sin(\theta/2)  \\ 0 & \cos(\theta/2) & -i\sin(\theta/2) & 0 \\ 0 & -i\sin(\theta/2) & \cos(\theta/2) & 0 \\ -i\sin(\theta/2) & 0 & 0 & \cos(\theta/2) \end{bmatrix}\quad`
   * - |RYY|                                                        
     - ``RYY``
     - :math:`\begin{bmatrix} \cos(\theta/2) & 0 & 0 & i\sin(\theta/2)  \\ 0 & \cos(\theta/2) & -i\sin(\theta/2) & 0 \\ 0 & -i\sin(\theta/2) & \cos(\theta/2) & 0 \\ i\sin(\theta/2) & 0 & 0 & \cos(\theta/2) \end{bmatrix}\quad`
   * - |RZZ|                                                        
     - ``RZZ``
     - :math:`\begin{bmatrix} \exp(-i\theta/2) & 0 & 0 & 0  \\ 0 & \exp(i\theta/2) & 0 & 0 \\ 0 & 0 & \exp(i\theta/2) & 0 \\ 0 & 0 & 0 & \exp(-i\theta/2) \end{bmatrix}\quad`
   * - |RZX|                                                        
     - ``RZX``
     - :math:`\begin{bmatrix} \cos(\theta/2) & 0 & -i\sin(\theta/2) & 0  \\ 0 & \cos(\theta/2) & 0 & i\sin(\theta/2) \\ -i\sin(\theta/2) & 0 & \cos(\theta/2) & 0 \\ 0 & i\sin(\theta/2) & 0 & \cos(\theta/2) \end{bmatrix}\quad`
   * - |Toffoli|                                                    
     - ``Toffoli``               
     - :math:`\begin{bmatrix} 1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 \\ 0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 & 1 & 0 & 0 & 0  \\ 0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 \\ 0 & 0 & 0 & 0 & 0 & 0 & 0 & 1  \\ 0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 \\ \end{bmatrix}\quad`
