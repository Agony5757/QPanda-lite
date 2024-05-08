import json
import matplotlib.pyplot as plt
import numpy as np

# # Load the dictionary from the JSON file
# with open(r'C:\Users\RGZN90601\Desktop\QPanda-lite\data_sup.json', 'r') as file:
#     data_sup = json.load(file)
# with open(r'C:\Users\RGZN90601\Desktop\QPanda-lite\data_normal.json', 'r') as file:
#     data_normal = json.load(file)

# # Assuming 'data' is your dictionary and 'k_values' are the keys as floats
# k_values_sup = [float(k) for k in data_sup.keys()]
# predicted_values_sup = [1 - (1 - 2 * k/3) for k in k_values_sup]
# # predicted_values_sup = [k/2 for k in k_values_sup]
# k_values_normal = [float(k) for k in data_normal.keys()]
# predicted_values_normal = [1 - (1 - 2 * k/3) for k in k_values_normal]

# # Invert the data by calculating 1 - value for each value in the datasets
# inverted_data_sup = {key: [1 - val for val in values] for key, values in data_sup.items()}
# inverted_data_normal = {key: [1 - val for val in values] for key, values in data_normal.items()}

# plt.figure(figsize=(12, 8))

# # Create the first subplot with shared y-axis
# ax1 = plt.subplot(1, 2, 1)
# plt.boxplot(inverted_data_sup.values(), labels=inverted_data_sup.keys())
# plt.plot(range(1, len(predicted_values_sup) + 1), predicted_values_sup, 'g-o', label='Predicted Suppressed')
# plt.legend()
# plt.title('(1 - F) Infidelity Error Suppression')
# plt.xlabel('Depolarization Strength')
# plt.ylabel('Value')
# # plt.yscale('log')

# # Create the second subplot, sharing the y-axis with the first
# ax2 = plt.subplot(1, 2, 2, sharey=ax1)
# plt.boxplot(inverted_data_normal.values(), labels=inverted_data_normal.keys())
# plt.plot(range(1, len(predicted_values_normal) + 1), predicted_values_normal, 'g-o', label='Predicted Normal')
# plt.title('(1 - F) Infidelity Raw Circuit')
# plt.xlabel('Depolarization Strength')

# # Hide y-axis labels on the second plot to avoid label duplication
# plt.setp(ax2.get_yticklabels(), visible=False)
# plt.legend()
# plt.tight_layout()
# plt.show()

# Data
# Given data
x = [1e-1, 5e-2, 1e-2, 5e-3, 1e-3, 5e-4, 1e-4]
p = np.array(x)
predicted_raw = 2 * p / 3
predicted_suppression = 1 - (1 - p + 2 * p**2 / 9) / (1 + 2 * p * (2 * p - 3) / 9)

suppression = [0.038031953888349034, 0.017755342411343078, 0.003380587203426303, 
               0.0016816904917188412, 0.0003341679612717067, 0.00016901651807362436, 
               3.560617082634665e-05]
raw = [0.06665436426798499, 0.03324747085571289, 0.006716569264729855, 
       0.0033316612243652344, 0.0006745656331380578, 0.0003256797790527344, 
       6.516774495446409e-05]

# Calculate the ratio of suppression to raw
ratio = np.array(suppression) / np.array(raw)
predicted_ratio = predicted_suppression / predicted_raw

# Create subplots
fig, axs = plt.subplots(1, 2, figsize=(15, 6))

# First subplot for Suppression, Raw, and their predicted values
axs[0].scatter(x, suppression, label='Suppression', marker='o')
axs[0].scatter(x, raw, label='Raw', marker='o')
axs[0].plot(x, predicted_suppression, label='Predicted Suppression', marker='x', linestyle='--')
axs[0].plot(x, predicted_raw, label='Predicted Raw', marker='x', linestyle='--')
axs[0].set_xscale('log')
axs[0].set_yscale('log')
axs[0].set_title('Suppression and Raw with Predictions')
axs[0].set_xlabel('Depolarization Strength')
axs[0].set_ylabel('Value')
axs[0].legend()
axs[0].grid(True)

# Second subplot for Suppression/Raw ratio
axs[1].scatter(x, ratio, label='Suppression/Raw Ratio', marker='o', color='red')
axs[1].plot(x, predicted_ratio, label='Predicted Ratio', marker='x', linestyle='--')
axs[1].set_xscale('log')
axs[1].set_title('Suppression/Raw Ratio')
axs[1].set_xlabel('Depolarization Strength')
axs[1].set_ylabel('Ratio')
axs[1].legend()
axs[1].grid(True)

plt.tight_layout()
plt.show()