#
# Utilities for working with YAML and JSON data representations.
#
# NOTE: The core utilities treat the YAML and JSON representations as equivalent.  This may
# not be true in general, but it is true for their application within PyUtilib.
#

__all__ = ['yaml_fix', 'json_fix', 'load_yaml', 'load_json', 'extract_subtext',
           'compare_repn', 'compare_strings', 'compare_yaml_files',
           'compare_json_files', 'simple_yaml_parser']

import pprint
import math
import re
import sys
try:
    unicode
except:
    basestring = str
try:  # pragma no cover
    from collections import OrderedDict
except ImportError:  # pragma no cover
    from ordereddict import OrderedDict
try:
    from StringIO import StringIO
except:
    from io import StringIO

from pyutilib.misc.comparison import open_possibly_compressed_file


def yaml_eval(str):
    try:
        val = int(str)
        return val
    except:
        pass
    try:
        val = float(str)
        return val
    except:
        pass
    try:
        val = eval(str)
        return val
    except:
        pass
    return str


def recursive_yaml_parser(stream, _depth=-1):
    depth = -1
    data = None
    for Line in stream:
        line = Line
        flag = True
        while flag:
            flag = False
            if line.strip() == '':
                continue
            if line.strip() == '---':
                continue
            if line.strip() == '...':
                break
            d = 0
            while d < len(line) and line[d] == ' ':
                d += 1
            if line[d] == '#':
                continue
            if depth == -1:
                if d <= _depth:
                    return None, line
                depth = d
            #if d >= depth:
            #depth = d
            if d < depth:
                return data, line
            if d >= depth:
                if line[d] == '-':
                    if data is None:
                        data = []
                    value = line[d + 1:].strip()
                    if len(value) > 0:
                        data.append(yaml_eval(value))
                    else:
                        value, line = recursive_yaml_parser(stream, d)
                        flag = True
                        data.append(value)
                else:
                    if data is None:
                        data = {}
                    tokens = line.split(':')
                    key = tokens[0].strip()
                    value = tokens[1].strip()
                    if len(value) > 0:
                        data[key] = yaml_eval(value)
                    else:
                        value, line = recursive_yaml_parser(stream, d)
                        flag = True
                        data[key] = value
    return data, line


def simple_yaml_parser(stream):
    if isinstance(stream, basestring):
        _stream = open_possibly_compressed_file(stream)
        repn = recursive_yaml_parser(_stream)[0]
        _stream.close()
        return repn
    return recursive_yaml_parser(stream)[0]


def yaml_fix(val):
    if not isinstance(val, basestring):
        return val
    return val.replace(':', '\\x3a')


def json_fix(val):
    return yaml_fix(val)


def extract_subtext(stream, begin_str='', end_str=None, comment='#'):
    if isinstance(stream, basestring):
        _stream = open_possibly_compressed_file(stream)
    else:
        _stream = stream
    if end_str is None:
        end_str == begin_str
    ans = []
    status = len(begin_str) == 0
    for line in _stream:
        tokens = re.split('[\t ]+', line.strip())
        if not status and line.startswith(begin_str):
            status = True
        elif not end_str is None and end_str != '' and line.startswith(end_str):
            break
        elif status:
            if tokens[0] != comment:
                ans.append(line)
    if isinstance(stream, basestring):
        _stream.close()
    return "".join(ans)


def load_yaml(str):
    import yaml
    istream = StringIO(str)
    return yaml.load(istream, Loader=yaml.SafeLoader)


def load_json(str):
    import json

    def _to_list(data):
        ans = []
        if sys.version_info < (3, 0):
            for val in data:
                val_type = type(val)
                if val_type is unicode:
                    val = val.encode('utf-8')
                elif val_type is dict:
                    val = _to_dict(val)
                elif val_type is list:
                    val = _to_list(val)
                ans.append(val)
        else:
            for val in data:
                val_type = type(val)
                if val_type is bytes:
                    val = val.encode('utf-8')
                elif val_type is dict:
                    val = _to_dict(val)
                elif val_type is list:
                    val = _to_list(val)
                ans.append(val)
        return ans

    def _to_dict(data):
        ans = {}
        if sys.version_info < (3, 0):
            for key, val in data.iteritems():
                if type(key) is unicode:
                    key = key.encode('utf-8')
                val_type = type(val)
                if val_type is unicode:
                    val = val.encode('utf-8')
                elif val_type is dict:
                    val = _to_dict(val)
                elif val_type is list:
                    val = _to_list(val)
                ans[key] = val
        else:
            for key, val in data.items():
                if type(key) is bytes:
                    key = key.encode('utf-8')
                val_type = type(val)
                if val_type is bytes:
                    val = val.encode('utf-8')
                elif val_type is dict:
                    val = _to_dict(val)
                elif val_type is list:
                    val = _to_list(val)
                ans[key] = val
        return ans

    # Use specialized decoders because JSON returns UNICODE strings,
    # regardless of what string was originally encoded.  We convert 
    # all unicode back to plain str.
    return json.loads(str, object_hook=_to_dict)


def compare_repn(baseline,
                 output,
                 tolerance=0.0,
                 prefix="<root>",
                 exact=True,
                 using_yaml=True):
    if type(baseline) != type(output) and not (
            type(baseline) in [int, float] and type(output) in [int, float]):
        raise IOError(
            "(%s) Structural difference:\nbaseline:\n%s\noutput:\n%s" %
            (prefix, pprint.pformat(baseline), pprint.pformat(output)))
    #
    if type(baseline) is list:
        if not exact and len(baseline) > len(output):
            raise IOError(
                "(%s) Baseline has longer list than output:\nbaseline:\n%s\noutput:\n%s"
                % (prefix, pprint.pformat(baseline), pprint.pformat(output)))
        if exact and len(baseline) != len(output):
            raise IOError(
                "(%s) Baseline list length does not equal output list:\nbaseline:\n%s\noutput:\n%s"
                % (prefix, pprint.pformat(baseline), pprint.pformat(output)))
        j = 0
        i = 0
        msg = ''
        while j < len(baseline) and i < len(output):
            try:
                compare_repn(
                    baseline[j],
                    output[i],
                    tolerance=tolerance,
                    prefix=prefix + "[" + str(i) + "]",
                    exact=exact,
                    using_yaml=using_yaml)
                j += 1
            except Exception:
                msg = sys.exc_info()[1]
                print(msg)
                pass
            i += 1
        if j < len(baseline):
            raise IOError(
                "(%s) Could not find item %d in output list:\nbaseline:\n%s\noutput:\n%s\nERROR: %s"
                % (prefix, j, pprint.pformat(baseline), pprint.pformat(output),
                   msg))
    #
    elif type(baseline) is dict or type(baseline) is OrderedDict:
        if exact and len(baseline.keys()) != len(output.keys()):
            raise IOError(
                "(%s) Baseline and output have different keys:\nbaseline:\n%s\noutput:\n%s"
                % (prefix, pprint.pformat(baseline.keys()),
                   pprint.pformat(output.keys())))
        for key in baseline:
            if not key in output:
                raise IOError(
                    "(%s) Baseline key %s that does not exist in output:baseline:\n%s\noutput:\n%s"
                    % (prefix, key, pprint.pformat(baseline.keys()),
                       pprint.pformat(output.keys())))
            compare_repn(
                baseline[key],
                output[key],
                tolerance=tolerance,
                prefix=prefix + "." + str(key),
                exact=exact,
                using_yaml=using_yaml)
    #
    elif (type(baseline) is float or type(output) is float
         ) and type(baseline) in [int, float] and type(output) in [int, float]:
        if not tolerance is None and math.fabs(baseline - output) > tolerance:
            raise ValueError(
                "(%s) Floating point values differ: baseline=%.17g and output=%.17g (tolerance=%.17g)"
                % (prefix, baseline, output, tolerance))
    elif baseline != output:  #pragma:nocover
        raise ValueError("(%s) Values differ:\nbaseline:\n%s\noutput:\n%s" % (
            prefix, pprint.pformat(baseline), pprint.pformat(output)))


def compare_strings(baseline,
                    output,
                    tolerance=0.0,
                    exact=True,
                    using_yaml=True):
    if using_yaml:
        try:
            baseline_repn = load_yaml(baseline)
            output_repn = load_yaml(output)
        except ImportError:
            raise IOError(
                "Cannot compare YAML strings because YAML is not available")
    else:
        try:
            baseline_repn = load_json(baseline)
        except ImportError:
            raise IOError(
                "Cannot compare JSON strings because JSON is not available")
        except Exception:
            print("Problem parsing JSON baseline")
            print(baseline)
            raise
        try:
            output_repn = load_json(output)
        except Exception:
            print("Problem parsing JSON output")
            print(output)
            raise
    compare_repn(
        baseline_repn,
        output_repn,
        tolerance=tolerance,
        exact=exact,
        using_yaml=using_yaml)


def compare_files(baseline_fname,
                  output_fname,
                  tolerance=0.0,
                  baseline_begin='',
                  baseline_end='',
                  output_begin='',
                  output_end=None,
                  exact=True,
                  using_yaml=True):
    INPUT = open_possibly_compressed_file(baseline_fname)
    baseline = extract_subtext(
        INPUT, begin_str=baseline_begin, end_str=baseline_end)
    INPUT.close()
    INPUT = open_possibly_compressed_file(output_fname)
    output = extract_subtext(INPUT, begin_str=output_begin, end_str=output_end)
    INPUT.close()
    compare_strings(
        baseline,
        output,
        tolerance=tolerance,
        exact=exact,
        using_yaml=using_yaml)


def compare_json_files(baseline_fname,
                       output_fname,
                       tolerance=0.0,
                       baseline_begin='',
                       baseline_end='',
                       output_begin='',
                       output_end=None,
                       exact=True):
    return compare_files(
        baseline_fname,
        output_fname,
        tolerance=tolerance,
        baseline_begin=baseline_begin,
        baseline_end=baseline_end,
        output_begin=output_begin,
        output_end=output_end,
        exact=exact,
        using_yaml=False)


def compare_yaml_files(baseline_fname,
                       output_fname,
                       tolerance=0.0,
                       baseline_begin='',
                       baseline_end='',
                       output_begin='',
                       output_end=None,
                       exact=True):
    return compare_files(
        baseline_fname,
        output_fname,
        tolerance=tolerance,
        baseline_begin=baseline_begin,
        baseline_end=baseline_end,
        output_begin=output_begin,
        output_end=output_end,
        exact=exact,
        using_yaml=True)
