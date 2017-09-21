module CustomHelpers
	def is_current_page(path)
		current_page.path == path ? " active" : ""
    end
    def cycle(index, arg0, arg1)
		index % 2 == 0 ? arg0 : arg1
    end
end
