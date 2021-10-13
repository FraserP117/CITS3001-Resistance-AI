
def sort_dict_by_value(D):
      sorted_values = sorted(D.values()) # Sort the values
      sorted_dict = {}

      for i in sorted_values:
          for k in D.keys():
              if D[k] == i:
                  sorted_dict[k] = D[k]
                  break

      return sorted_dict

def dict_max_by_value(D):
    sorted = sort_dict_by_value(D)
    return (list(sorted)[-1], D[list(sorted)[-1]])


if __name__ == '__main__':
    pass
