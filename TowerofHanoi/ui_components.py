import streamlit as st

# Render the Tower of Hanoi game board
def render_game_board(state, n, pegs=3):
    max_disk_width = 140  # Reduced from 180 to make pegs smaller
    base_width = max_disk_width + 40  # Reduced from 60
    
    # Create CSS for the game board
    st.markdown("""
<style>
    body {
    background-color: #1e1e1e;
}

.game-board {
    display: flex;
    justify-content: center;
    align-items: flex-end;
    padding: 20px 0;
    background-color: #1e1e1e;
}

.tower {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 0 20px;  /* Reduced from 30px */
    position: relative;
}

.peg {
    width: 8px;  /* Reduced from 10px */
    background: linear-gradient(180deg, #ff4e50, #6b5b95);
    border-radius: 4px;  /* Reduced from 5px */
    margin-bottom: 8px;  /* Reduced from 10px */
}

.disk {
    border-radius: 18px;  /* Reduced from 20px */
    text-align: center;
    color: white;
    font-weight: bold;
    height: 26px;  /* Reduced from 28px */
    line-height: 26px;  /* Reduced from 28px */
    box-shadow: 0 0 6px rgba(0,0,0,0.5);
    margin: 4px 0;  /* Reduced from 5px */
    transition: all 0.3s ease;
    cursor: grab;
}

.disk:hover {
    transform: scale(1.05);
    box-shadow: 0 0 10px rgba(255,255,255,0.3);
}

.disk.dragging {
    opacity: 0.5;
    cursor: grabbing;
}

.base {
    background: linear-gradient(90deg, #ff4e50, #6b5b95);
    height: 10px;  /* Reduced from 12px */
    border-radius: 5px;  /* Reduced from 6px */
    margin-top: 8px;  /* Reduced from 10px */
}

.tower-label {
    color: white;
    font-size: 18px;  /* Reduced from 20px */
    margin-top: 8px;  /* Reduced from 10px */
}

.droppable {
    transition: all 0.3s ease;
}

.droppable.highlight {
    background-color: rgba(255,255,255,0.1);
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)

    
    # Draw the board
    cols = st.columns(pegs)
    peg_names = ['A', 'B', 'C', 'D'][:pegs]
    
    board_html = '<div class="game-board">'
    
    for i, peg in enumerate(peg_names):
        tower_html = f'<div class="tower" id="tower-{peg}" data-peg="{peg}">'
        
        # Calculate peg height based on number of disks
        peg_height = (n * 28) + 20  # Reduced slightly
        tower_html += f'<div class="peg droppable" id="peg-{peg}" style="height: {peg_height}px;" data-peg="{peg}"></div>'
        
        # Add disks
        disks_html = ""
        reversed_disks = reversed(state[peg])
        for disk in reversed_disks:
            # Calculate disk width proportional to its size
            disk_width = 30 + ((disk / n) * max_disk_width)
            # Generate a color based on disk size
            hue = int(120 + (240 * (disk / n)))
            disks_html += f'<div class="disk" id="disk-{disk}" data-size="{disk}" data-peg="{peg}" draggable="true" style="width: {disk_width}px; background-color: hsl({hue}, 70%, 50%);">{disk}</div>'
        
        tower_html += disks_html
        
        # Add base
        tower_html += f'<div class="base" style="width: {base_width}px;"></div>'
        tower_html += f'<div style="text-align: center; margin-top: 8px;"><h3>{peg}</h3></div>'
        tower_html += '</div>'
        
        board_html += tower_html
    
    board_html += '</div>'
    
    # Render the game board
    st.markdown(board_html, unsafe_allow_html=True)
    
    # Add JavaScript for drag and drop functionality
    drag_drop_js = """
    <script>
    // Wait for DOM to fully load
    document.addEventListener('DOMContentLoaded', function() {
        // Set up variables to store the drag state
        let draggedDisk = null;
        let sourcePeg = null;
        
        // Add event listeners to all disks
        const disks = document.querySelectorAll('.disk');
        disks.forEach(disk => {
            disk.addEventListener('dragstart', handleDragStart);
            disk.addEventListener('dragend', handleDragEnd);
        });
        
        // Add event listeners to all pegs
        const pegs = document.querySelectorAll('.droppable');
        pegs.forEach(peg => {
            peg.addEventListener('dragover', handleDragOver);
            peg.addEventListener('dragenter', handleDragEnter);
            peg.addEventListener('dragleave', handleDragLeave);
            peg.addEventListener('drop', handleDrop);
        });
        
        // Drag start handler
        function handleDragStart(e) {
            // Only allow dragging the top disk on a peg
            const peg = this.getAttribute('data-peg');
            const pegs = Array.from(document.querySelectorAll(`[data-peg="${peg}"]`));
            const disksOnPeg = pegs.filter(item => item.classList.contains('disk'));
            
            // If this is not the top disk, don't allow dragging
            if (disksOnPeg.length > 0 && disksOnPeg[0] !== this) {
                e.preventDefault();
                return false;
            }
            
            // Set drag data
            draggedDisk = this;
            sourcePeg = peg;
            this.classList.add('dragging');
            
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', this.id);
            
            // For better visual feedback
            setTimeout(() => {
                this.style.opacity = '0.4';
            }, 0);
            
            return true;
        }
        
        // Drag end handler
        function handleDragEnd() {
            this.classList.remove('dragging');
            this.style.opacity = '1';
            
            // Reset highlight on all drop targets
            document.querySelectorAll('.droppable').forEach(peg => {
                peg.classList.remove('highlight');
            });
        }
        
        // Drag over handler
        function handleDragOver(e) {
            if (e.preventDefault) {
                e.preventDefault(); // Allows us to drop
            }
            e.dataTransfer.dropEffect = 'move';
            return false;
        }
        
        // Drag enter handler
        function handleDragEnter() {
            this.classList.add('highlight');
        }
        
        // Drag leave handler
        function handleDragLeave() {
            this.classList.remove('highlight');
        }
        
        // Drop handler
        function handleDrop(e) {
            e.stopPropagation(); // Stops browser from redirecting
            
            // If no disk is being dragged, do nothing
            if (!draggedDisk) return false;
            
            // Get target peg
            const targetPeg = this.getAttribute('data-peg');
            
            // Don't do anything if dropping onto the same peg
            if (sourcePeg === targetPeg) {
                return false;
            }
            
            // Check if move is valid (smaller disk onto larger disk or empty peg)
            const targetPegElement = document.querySelector(`#peg-${targetPeg}`);
            const disksOnTargetPeg = Array.from(document.querySelectorAll(`[data-peg="${targetPeg}"].disk`));
            
            // If target peg has disks, check that the dragged disk is smaller than the top disk
            if (disksOnTargetPeg.length > 0) {
                const topDiskSize = parseInt(disksOnTargetPeg[0].getAttribute('data-size'));
                const draggedDiskSize = parseInt(draggedDisk.getAttribute('data-size'));
                
                if (draggedDiskSize >= topDiskSize) {
                    // Invalid move: can't place larger disk on smaller disk
                    return false;
                }
            }
            
            // Update disk's data-peg attribute
            draggedDisk.setAttribute('data-peg', targetPeg);
            
            // Add the move to a hidden input to track the sequence
            const moveInput = document.getElementById('move-sequence') || createMoveSequenceInput();
            const currentSequence = moveInput.value;
            const newMove = `${sourcePeg}->${targetPeg}`;
            moveInput.value = currentSequence ? `${currentSequence},${newMove}` : newMove;
            
            // Visually, we would need to append the disk to the target peg
            // This example uses Streamlit which reloads on interaction
            // In a real implementation, you'd update the DOM here
            
            // Trigger a Streamlit event to update the game state
            if (window.parent.window.streamlitPythonInteractor) {
                const moveData = {
                    source: sourcePeg,
                    destination: targetPeg
                };
                window.parent.window.streamlitPythonInteractor.sendDataToPython({
                    type: 'hanoi-move',
                    data: moveData
                });
            }
            
            // Fallback to form submission for Streamlit
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '';
            
            const sourceInput = document.createElement('input');
            sourceInput.type = 'hidden';
            sourceInput.name = 'source';
            sourceInput.value = sourcePeg;
            form.appendChild(sourceInput);
            
            const destInput = document.createElement('input');
            destInput.type = 'hidden';
            destInput.name = 'destination';
            destInput.value = targetPeg;
            form.appendChild(destInput);
            
            document.body.appendChild(form);
            form.submit();
            
            return false;
        }
        
        // Helper function to create a hidden input for move sequence
        function createMoveSequenceInput() {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.id = 'move-sequence';
            input.name = 'move-sequence';
            document.body.appendChild(input);
            return input;
        }
    });
    </script>
    """
    
    st.components.v1.html(drag_drop_js, height=0)