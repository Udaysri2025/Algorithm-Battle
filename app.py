from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__, static_folder='.', static_url_path='', template_folder='.')

# ---------- Algorithm Generators ----------

def bubble_sort_steps(arr):
    arr = arr[:]
    n = len(arr)
    comparisons = 0
    swaps = 0
    array_accesses = 0
    steps = []
    for i in range(n):
        for j in range(0, n - i - 1):
            comparisons += 1
            array_accesses += 2
            steps.append({"type": "compare", "indices": [j, j+1], "stats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}})
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
                swaps += 1
                array_accesses += 4
                steps.append({"type": "swap", "indices": [j, j+1], "array": arr[:], "stats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}})
        steps.append({"type": "sorted", "index": n - i - 1, "stats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}})
    return {"steps": steps, "finalStats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}}

def insertion_sort_steps(arr):
    arr = arr[:]
    n = len(arr)
    comparisons = 0
    swaps = 0
    array_accesses = 0
    steps = []
    for i in range(1, n):
        key = arr[i]
        array_accesses += 1
        j = i - 1
        steps.append({"type": "compare", "indices": [i, j], "stats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}})
        while j >= 0 and arr[j] > key:
            comparisons += 1
            array_accesses += 2
            steps.append({"type": "compare", "indices": [j, j+1], "stats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}})
            arr[j+1] = arr[j]
            swaps += 1
            array_accesses += 2
            steps.append({"type": "swap", "indices": [j, j+1], "array": arr[:], "stats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}})
            j -= 1
        arr[j+1] = key
        swaps += 1
        array_accesses += 1
        steps.append({"type": "swap", "indices": [j+1, i], "array": arr[:], "stats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}})
    for k in range(n):
        steps.append({"type": "sorted", "index": k, "stats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}})
    return {"steps": steps, "finalStats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}}

def selection_sort_steps(arr):
    arr = arr[:]
    n = len(arr)
    comparisons = 0
    swaps = 0
    array_accesses = 0
    steps = []
    for i in range(n):
        min_idx = i
        steps.append({"type": "pivot", "index": i, "stats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}})
        for j in range(i+1, n):
            comparisons += 1
            array_accesses += 2
            steps.append({"type": "compare", "indices": [min_idx, j], "stats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}})
            if arr[j] < arr[min_idx]:
                min_idx = j
                steps.append({"type": "pivot", "index": min_idx, "stats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}})
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            swaps += 1
            array_accesses += 4
            steps.append({"type": "swap", "indices": [i, min_idx], "array": arr[:], "stats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}})
        steps.append({"type": "sorted", "index": i, "stats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}})
    return {"steps": steps, "finalStats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}}

def quick_sort_steps(arr):
    arr = arr[:]
    comparisons = 0
    swaps = 0
    array_accesses = 0
    steps = []
    
    def _partition(low, high):
        nonlocal comparisons, swaps, array_accesses
        pivot = arr[high]
        array_accesses += 1
        i = low - 1
        steps.append({"type": "pivot", "index": high, "stats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}})
        for j in range(low, high):
            comparisons += 1
            array_accesses += 2
            steps.append({"type": "compare", "indices": [j, high], "stats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}})
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
                swaps += 1
                array_accesses += 4
                steps.append({"type": "swap", "indices": [i, j], "array": arr[:], "stats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}})
        arr[i+1], arr[high] = arr[high], arr[i+1]
        swaps += 1
        array_accesses += 4
        steps.append({"type": "swap", "indices": [i+1, high], "array": arr[:], "stats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}})
        steps.append({"type": "sorted", "index": i+1, "stats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}})
        return i+1

    def _quick_sort(low, high):
        if low < high:
            pi = _partition(low, high)
            _quick_sort(low, pi - 1)
            _quick_sort(pi + 1, high)
        elif low == high:
            steps.append({"type": "sorted", "index": low, "stats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}})

    _quick_sort(0, len(arr)-1)
    return {"steps": steps, "finalStats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}}

def merge_sort_steps(arr):
    arr = arr[:]
    comparisons = 0
    swaps = 0
    array_accesses = 0
    steps = []
    aux = arr[:]

    def _merge(l, m, r):
        nonlocal comparisons, swaps, array_accesses
        for i in range(l, r+1):
            aux[i] = arr[i]
            array_accesses += 2
        i, j, k = l, m+1, l
        while i <= m and j <= r:
            comparisons += 1
            array_accesses += 2
            steps.append({"type": "compare", "indices": [i, j], "stats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}})
            if aux[i] <= aux[j]:
                arr[k] = aux[i]
                i += 1
            else:
                arr[k] = aux[j]
                j += 1
            swaps += 1
            array_accesses += 2
            steps.append({"type": "swap", "indices": [k], "array": arr[:], "stats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}})
            k += 1
        while i <= m:
            arr[k] = aux[i]
            swaps += 1
            array_accesses += 2
            steps.append({"type": "swap", "indices": [k], "array": arr[:], "stats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}})
            i += 1
            k += 1
        while j <= r:
            arr[k] = aux[j]
            swaps += 1
            array_accesses += 2
            steps.append({"type": "swap", "indices": [k], "array": arr[:], "stats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}})
            j += 1
            k += 1
        for idx in range(l, r+1):
            steps.append({"type": "sorted", "index": idx, "stats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}})

    def _merge_sort(l, r):
        if l < r:
            m = (l + r) // 2
            _merge_sort(l, m)
            _merge_sort(m+1, r)
            _merge(l, m, r)
        elif l == r:
            steps.append({"type": "sorted", "index": l, "stats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}})

    _merge_sort(0, len(arr)-1)
    return {"steps": steps, "finalStats": {"comparisons": comparisons, "swaps": swaps, "array_accesses": array_accesses}}

# Algorithm metadata
ALGORITHMS = {
    "bubble": {"func": bubble_sort_steps, "name": "Bubble Sort", "color": "#ef4444"},
    "insertion": {"func": insertion_sort_steps, "name": "Insertion Sort", "color": "#f59e0b"},
    "selection": {"func": selection_sort_steps, "name": "Selection Sort", "color": "#8b5cf6"},
    "quick": {"func": quick_sort_steps, "name": "Quick Sort", "color": "#10b981"},
    "merge": {"func": merge_sort_steps, "name": "Merge Sort", "color": "#3b82f6"}
}

# Input presets
def generate_array(size, preset):
    if preset == "random":
        return [random.randint(20, 400) for _ in range(size)]
    elif preset == "nearly_sorted":
        arr = list(range(20, 20 + size * 3, 3))
        for _ in range(size // 10):
            i, j = random.randint(0, size-1), random.randint(0, size-1)
            arr[i], arr[j] = arr[j], arr[i]
        return arr[:size]
    elif preset == "reversed":
        return list(range(400, 20, -380 // size))[:size]
    elif preset == "few_unique":
        return [random.choice([50, 150, 300]) for _ in range(size)]
    return [random.randint(20, 400) for _ in range(size)]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_battle():
    data = request.json
    algo_a = data['algoA']
    algo_b = data['algoB']
    array = data.get('array')
    size = data.get('size', 50)
    preset = data.get('preset', 'random')
    
    if not array:
        array = generate_array(size, preset)
    else:
        array = array[:]
    
    result_a = ALGORITHMS[algo_a]["func"](array)
    result_b = ALGORITHMS[algo_b]["func"](array)
    
    return jsonify({
        "array": array,
        "algoA": {
            "name": ALGORITHMS[algo_a]["name"],
            "color": ALGORITHMS[algo_a]["color"],
            "steps": result_a["steps"],
            "finalStats": result_a["finalStats"]
        },
        "algoB": {
            "name": ALGORITHMS[algo_b]["name"],
            "color": ALGORITHMS[algo_b]["color"],
            "steps": result_b["steps"],
            "finalStats": result_b["finalStats"]
        }
    })

if __name__ == '__main__':
    app.run(debug=True)